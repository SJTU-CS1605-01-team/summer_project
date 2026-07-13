from __future__ import annotations

import csv
import json
import math
import os
import sys
from collections import OrderedDict

from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor, QFont
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsCoordinateReferenceSystem,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsFillSymbol,
    QgsGradientColorRamp,
    QgsGraduatedSymbolRenderer,
    QgsLayoutExporter,
    QgsLayoutItemLabel,
    QgsLayoutItemLegend,
    QgsLayoutItemMap,
    QgsLayoutItemScaleBar,
    QgsLayoutMeasurement,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsLegendStyle,
    QgsPrintLayout,
    QgsProject,
    QgsRectangle,
    QgsRendererRangeLabelFormat,
    QgsSingleSymbolRenderer,
    QgsUnitTypes,
    QgsVectorFileWriter,
    QgsVectorLayer,
)


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STAGE_DIR = os.path.dirname(SCRIPT_DIR)
TORONTO_DIR = os.path.join(STAGE_DIR, "Toronto_data")
PROCESSED_DIR = os.path.join(TORONTO_DIR, "processed")
MAPS_DIR = os.path.join(STAGE_DIR, "maps")
STYLES_DIR = os.path.join(SCRIPT_DIR, "styles")

STAGE4_GPKG = os.path.join(PROCESSED_DIR, "toronto_stage4.gpkg")
NATIONAL_CSV = os.path.join(PROCESSED_DIR, "canada_ct_10_indicators_2021.csv")
TORONTO_CSV = os.path.join(PROCESSED_DIR, "toronto_indicators_2021.csv")
SUMMARY_CSV = os.path.join(PROCESSED_DIR, "stage5_join_summary.csv")
COVERAGE_CSV = os.path.join(PROCESSED_DIR, "stage5_indicator_coverage.csv")
OUTPUT_GPKG = os.path.join(PROCESSED_DIR, "city_tract_indicators.gpkg")
PROJECT_PATH = os.path.join(SCRIPT_DIR, "toronto_stage5_6.qgz")
SUMMARY_JSON = os.path.join(PROCESSED_DIR, "stage5_6_build_summary.json")

INDICATOR_FIELDS = [
    "population_2021",
    "population_density_km2",
    "age_65_plus_pct",
    "average_household_size",
    "median_total_income_2020",
    "low_income_lim_at_pct",
    "renter_households_pct",
    "shelter_cost_30pct_plus_pct",
    "bachelor_or_higher_age25_64_pct",
    "unemployment_rate_pct",
]

CSV_METADATA_FIELDS = [
    "CENSUS_YEAR",
    "ALT_GEO_CODE",
    "GEO_LEVEL",
    "GEO_NAME",
    "DATA_QUALITY_FLAG",
]


def require(path: str) -> None:
    if not os.path.exists(path):
        raise FileNotFoundError(path)


def parse_number(value: str | None) -> float | None:
    if value is None:
        return None
    value = value.strip()
    if value == "":
        return None
    try:
        result = float(value)
    except ValueError:
        return None
    return result if math.isfinite(result) else None


def write_csv(path: str, fieldnames: list[str], rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_layer(layer: QgsVectorLayer, path: str, layer_name: str, overwrite_file: bool) -> None:
    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "GPKG"
    options.layerName = layer_name
    options.fileEncoding = "UTF-8"
    options.actionOnExistingFile = (
        QgsVectorFileWriter.CreateOrOverwriteFile
        if overwrite_file
        else QgsVectorFileWriter.CreateOrOverwriteLayer
    )
    options.layerOptions = ["SPATIAL_INDEX=YES"] if layer.isSpatial() else []
    result = QgsVectorFileWriter.writeAsVectorFormatV3(
        layer,
        path,
        QgsProject.instance().transformContext(),
        options,
    )
    if result[0] != QgsVectorFileWriter.NoError:
        raise RuntimeError(f"Failed writing {layer_name}: {result}")


def make_outline_renderer(color: str = "#252525", width: float = 0.9) -> QgsSingleSymbolRenderer:
    symbol = QgsFillSymbol.createSimple(
        {
            "color": "255,255,255,0",
            "outline_color": color,
            "outline_width": str(width),
        }
    )
    return QgsSingleSymbolRenderer(symbol)


def make_nodata_renderer() -> QgsSingleSymbolRenderer:
    symbol = QgsFillSymbol.createSimple(
        {
            "color": "#d9d9d9",
            "outline_color": "#ffffff",
            "outline_width": "0.12",
        }
    )
    return QgsSingleSymbolRenderer(symbol)


def make_graduated_renderer(
    layer: QgsVectorLayer,
    field_name: str,
    start_color: str,
    end_color: str,
    precision: int,
) -> QgsGraduatedSymbolRenderer:
    base_symbol = QgsFillSymbol.createSimple(
        {
            "color": start_color,
            "outline_color": "#ffffff",
            "outline_width": "0.12",
        }
    )
    ramp = QgsGradientColorRamp(QColor(start_color), QColor(end_color))
    label_format = QgsRendererRangeLabelFormat("%1 – %2", precision)
    renderer = QgsGraduatedSymbolRenderer.createRenderer(
        layer,
        field_name,
        5,
        QgsGraduatedSymbolRenderer.Jenks,
        base_symbol,
        ramp,
        label_format,
    )
    if renderer is None:
        raise RuntimeError(f"Could not create renderer for {field_name}")
    renderer.setClassAttribute(field_name)
    for item in renderer.ranges():
        symbol = item.symbol()
        symbol.symbolLayer(0).setStrokeColor(QColor("#ffffff"))
        symbol.symbolLayer(0).setStrokeWidth(0.12)
    return renderer


def add_label(
    layout: QgsPrintLayout,
    text: str,
    x: float,
    y: float,
    w: float,
    h: float,
    size: float,
    bold: bool = False,
    color: str = "#222222",
) -> QgsLayoutItemLabel:
    label = QgsLayoutItemLabel(layout)
    label.setText(text)
    font = QFont("Segoe UI", size)
    font.setBold(bold)
    label.setFont(font)
    label.setFontColor(QColor(color))
    label.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    label.attemptResize(QgsLayoutSize(w, h, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(label)
    return label


def expanded_extent(layer: QgsVectorLayer, factor: float = 1.06) -> QgsRectangle:
    extent = QgsRectangle(layer.extent())
    extent.scale(factor)
    return extent


def create_layout(
    project: QgsProject,
    name: str,
    title: str,
    subtitle: str,
    main_layer: QgsVectorLayer,
    nodata_layer: QgsVectorLayer,
    boundary_layer: QgsVectorLayer,
    source_note: str,
    preview_stem: str,
) -> dict:
    old_layout = project.layoutManager().layoutByName(name)
    if old_layout:
        project.layoutManager().removeLayout(old_layout)

    layout = QgsPrintLayout(project)
    layout.initializeDefaults()
    layout.setName(name)
    page = layout.pageCollection().page(0)
    page.setPageSize(QgsLayoutSize(297, 210, QgsUnitTypes.LayoutMillimeters))

    add_label(layout, title, 10, 6, 277, 10, 20, True, "#1a1a1a")
    add_label(layout, subtitle, 10, 16, 277, 7, 9, False, "#4d4d4d")

    map_item = QgsLayoutItemMap(layout)
    map_item.attemptMove(QgsLayoutPoint(10, 26, QgsUnitTypes.LayoutMillimeters))
    map_item.attemptResize(QgsLayoutSize(205, 163, QgsUnitTypes.LayoutMillimeters))
    map_item.setFrameEnabled(True)
    map_item.setFrameStrokeColor(QColor("#666666"))
    map_item.setFrameStrokeWidth(QgsLayoutMeasurement(0.3, QgsUnitTypes.LayoutMillimeters))
    map_item.setLayers([boundary_layer, main_layer, nodata_layer])
    map_item.setExtent(expanded_extent(boundary_layer, 1.04))
    map_item.setKeepLayerSet(True)
    layout.addLayoutItem(map_item)

    legend = QgsLayoutItemLegend(layout)
    legend.setTitle("Legend")
    legend.setLinkedMap(map_item)
    legend.setLegendFilterByMapEnabled(True)
    legend.setAutoUpdateModel(True)
    legend.setStyleFont(QgsLegendStyle.Title, QFont("Segoe UI", 12, QFont.Bold))
    legend.setStyleFont(QgsLegendStyle.Subgroup, QFont("Segoe UI", 9, QFont.Bold))
    legend.setStyleFont(QgsLegendStyle.SymbolLabel, QFont("Segoe UI", 8))
    legend.attemptMove(QgsLayoutPoint(220, 27, QgsUnitTypes.LayoutMillimeters))
    legend.attemptResize(QgsLayoutSize(67, 82, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(legend)

    scale_bar = QgsLayoutItemScaleBar(layout)
    scale_bar.setStyle("Single Box")
    scale_bar.setLinkedMap(map_item)
    scale_bar.setUnits(QgsUnitTypes.DistanceKilometers)
    scale_bar.setNumberOfSegments(4)
    scale_bar.setNumberOfSegmentsLeft(0)
    scale_bar.setUnitsPerSegment(5)
    scale_bar.setUnitLabel("km")
    scale_bar.setFont(QFont("Segoe UI", 8))
    scale_bar.attemptMove(QgsLayoutPoint(15, 178, QgsUnitTypes.LayoutMillimeters))
    scale_bar.attemptResize(QgsLayoutSize(58, 8, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(scale_bar)

    add_label(layout, "N\n↑", 192, 31, 15, 23, 17, True, "#111111")
    add_label(
        layout,
        source_note,
        220,
        116,
        67,
        66,
        8,
        False,
        "#333333",
    )
    add_label(
        layout,
        "Projection: NAD83 / Statistics Canada Lambert (EPSG:3347)",
        10,
        193,
        277,
        6,
        7,
        False,
        "#555555",
    )
    add_label(
        layout,
        "Prepared for CS1605-01 Summer Project | Toronto Census Tracts",
        10,
        201,
        277,
        5,
        7,
        False,
        "#777777",
    )

    project.layoutManager().addLayout(layout)

    png_path = os.path.join(MAPS_DIR, preview_stem + "_preview.png")
    pdf_path = os.path.join(MAPS_DIR, preview_stem + "_preview.pdf")
    exporter = QgsLayoutExporter(layout)
    image_settings = QgsLayoutExporter.ImageExportSettings()
    image_settings.dpi = 300
    image_result = exporter.exportToImage(png_path, image_settings)
    pdf_settings = QgsLayoutExporter.PdfExportSettings()
    pdf_settings.dpi = 300
    pdf_result = exporter.exportToPdf(pdf_path, pdf_settings)
    if image_result != QgsLayoutExporter.Success:
        raise RuntimeError(f"Image export failed for {name}: {image_result}")
    if pdf_result != QgsLayoutExporter.Success:
        raise RuntimeError(f"PDF export failed for {name}: {pdf_result}")
    return {"name": name, "png": png_path, "pdf": pdf_path}


def main() -> None:
    for path in (STAGE4_GPKG, NATIONAL_CSV):
        require(path)
    for directory in (PROCESSED_DIR, MAPS_DIR, STYLES_DIR):
        os.makedirs(directory, exist_ok=True)

    app = QgsApplication([], False)
    app.initQgis()
    try:
        project = QgsProject.instance()
        project.clear()
        project.setCrs(QgsCoordinateReferenceSystem("EPSG:3347"))
        project.setFilePathStorage(Qgis.FilePathType.Relative)

        ct_raw = QgsVectorLayer(
            f"{STAGE4_GPKG}|layername=toronto_ct_2021_raw",
            "toronto_ct_2021_raw",
            "ogr",
        )
        city_source = QgsVectorLayer(
            f"{STAGE4_GPKG}|layername=toronto_city_boundary_2021",
            "toronto_city_boundary_2021",
            "ogr",
        )
        if not ct_raw.isValid() or not city_source.isValid():
            raise RuntimeError("Stage 4 GeoPackage layers could not be loaded")

        boundary_ids = []
        boundary_id_set = set()
        for feature in ct_raw.getFeatures():
            dguid = str(feature["DGUID"])
            boundary_ids.append(dguid)
            boundary_id_set.add(dguid)
        if len(boundary_ids) != len(boundary_id_set):
            raise RuntimeError("Duplicate DGUIDs in Toronto CT boundary")

        with open(NATIONAL_CSV, "r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            national_fields = list(reader.fieldnames or [])
            national_rows = list(reader)
        if "DGUID" not in national_fields:
            raise RuntimeError("DGUID missing from national CSV")

        all_indicator_ids = [row["DGUID"].strip() for row in national_rows]
        if len(all_indicator_ids) != len(set(all_indicator_ids)):
            raise RuntimeError("Duplicate DGUIDs in national indicator CSV")
        indicator_by_id = {row["DGUID"].strip(): row for row in national_rows}

        toronto_rows = [indicator_by_id[dguid] for dguid in sorted(boundary_id_set) if dguid in indicator_by_id]
        write_csv(TORONTO_CSV, national_fields, toronto_rows)

        toronto_indicator_ids = {row["DGUID"].strip() for row in toronto_rows}
        unmatched_boundaries = sorted(boundary_id_set - toronto_indicator_ids)
        unmatched_indicators = sorted(toronto_indicator_ids - boundary_id_set)
        matched_ids = boundary_id_set & toronto_indicator_ids
        match_rate = 100.0 * len(matched_ids) / len(boundary_id_set) if boundary_id_set else 0.0

        output_fields = QgsFields()
        for field in ct_raw.fields():
            output_fields.append(field)
        output_fields.append(QgsField("CENSUS_YEAR", QVariant.Int))
        output_fields.append(QgsField("ALT_GEO_CODE", QVariant.String, len=16))
        output_fields.append(QgsField("GEO_LEVEL", QVariant.String, len=32))
        output_fields.append(QgsField("GEO_NAME", QVariant.String, len=32))
        output_fields.append(QgsField("DATA_QUALITY_FLAG", QVariant.String, len=12))
        output_fields.append(QgsField("population_2021", QVariant.LongLong))
        for name in INDICATOR_FIELDS[1:]:
            output_fields.append(QgsField(name, QVariant.Double, len=20, prec=4))
        output_fields.append(QgsField("join_status", QVariant.String, len=16))
        output_fields.append(QgsField("join_matched", QVariant.Int))
        output_fields.append(QgsField("area_km2_calc", QVariant.Double, len=20, prec=6))
        output_fields.append(QgsField("pop_density_calc", QVariant.Double, len=20, prec=4))

        memory = QgsVectorLayer("MultiPolygon?crs=EPSG:3347", "city_tract_indicators", "memory")
        provider = memory.dataProvider()
        provider.addAttributes(output_fields)
        memory.updateFields()

        output_features = []
        density_differences = []
        for source_feature in ct_raw.getFeatures():
            dguid = str(source_feature["DGUID"])
            row = indicator_by_id.get(dguid)
            out = QgsFeature(memory.fields())
            out.setGeometry(source_feature.geometry())
            attrs = [source_feature[field.name()] for field in ct_raw.fields()]
            if row:
                census_year = int(row["CENSUS_YEAR"]) if row["CENSUS_YEAR"].strip() else None
                population = parse_number(row["population_2021"])
                metadata_values = [
                    census_year,
                    row["ALT_GEO_CODE"],
                    row["GEO_LEVEL"],
                    row["GEO_NAME"],
                    row["DATA_QUALITY_FLAG"],
                ]
                indicator_values = []
                for name in INDICATOR_FIELDS:
                    value = parse_number(row[name])
                    if name == "population_2021" and value is not None:
                        value = int(round(value))
                    indicator_values.append(value)
                join_status = "matched"
                join_matched = 1
            else:
                metadata_values = [None, None, None, None, None]
                indicator_values = [None] * len(INDICATOR_FIELDS)
                population = None
                join_status = "unmatched"
                join_matched = 0

            area_km2 = source_feature.geometry().area() / 1_000_000.0
            derived_density = (
                float(population) / area_km2
                if population is not None and area_km2 > 0
                else None
            )
            official_density = indicator_values[1] if row else None
            if derived_density is not None and official_density is not None:
                density_differences.append(derived_density - float(official_density))

            out.setAttributes(
                attrs
                + metadata_values
                + indicator_values
                + [join_status, join_matched, area_km2, derived_density]
            )
            output_features.append(out)

        provider.addFeatures(output_features)
        memory.updateExtents()
        if memory.featureCount() != ct_raw.featureCount():
            raise RuntimeError("Output feature count changed during join")

        write_layer(memory, OUTPUT_GPKG, "city_tract_indicators", True)
        write_layer(city_source, OUTPUT_GPKG, "toronto_city_boundary_2021", False)

        summary_rows = [
            OrderedDict(
                boundary_count=len(boundary_id_set),
                indicator_count=len(toronto_indicator_ids),
                matched_count=len(matched_ids),
                unmatched_boundary_count=len(unmatched_boundaries),
                unmatched_indicator_count=len(unmatched_indicators),
                match_rate_pct=f"{match_rate:.2f}",
                join_field_boundary="DGUID",
                join_field_indicators="DGUID",
                join_relationship="one_to_one",
            )
        ]
        write_csv(SUMMARY_CSV, list(summary_rows[0].keys()), summary_rows)

        coverage_rows = []
        for name in INDICATOR_FIELDS:
            non_missing = sum(1 for row in toronto_rows if parse_number(row[name]) is not None)
            missing = len(toronto_rows) - non_missing
            coverage_rows.append(
                OrderedDict(
                    indicator=name,
                    non_missing_count=non_missing,
                    missing_count=missing,
                    coverage_pct=f"{(100.0 * non_missing / len(toronto_rows)):.2f}",
                )
            )
        write_csv(COVERAGE_CSV, list(coverage_rows[0].keys()), coverage_rows)

        joined_source = f"{OUTPUT_GPKG}|layername=city_tract_indicators"
        joined_evidence = QgsVectorLayer(joined_source, "city_tract_indicators", "ogr")
        density = QgsVectorLayer(joined_source, "Population density (people per km²)", "ogr")
        density_nodata = QgsVectorLayer(joined_source, "No data", "ogr")
        low_income = QgsVectorLayer(joined_source, "Low-income prevalence (LIM-AT, %)", "ogr")
        low_income_nodata = QgsVectorLayer(joined_source, "No data", "ogr")
        boundary_density = QgsVectorLayer(
            f"{OUTPUT_GPKG}|layername=toronto_city_boundary_2021",
            "Toronto City boundary",
            "ogr",
        )
        boundary_low_income = QgsVectorLayer(
            f"{OUTPUT_GPKG}|layername=toronto_city_boundary_2021",
            "Toronto City boundary",
            "ogr",
        )
        for layer in (
            joined_evidence,
            density,
            density_nodata,
            low_income,
            low_income_nodata,
            boundary_density,
            boundary_low_income,
        ):
            if not layer.isValid():
                raise RuntimeError(f"Invalid output layer: {layer.name()}")

        density.setSubsetString('"pop_density_calc" IS NOT NULL')
        density_nodata.setSubsetString('"pop_density_calc" IS NULL')
        low_income.setSubsetString('"low_income_lim_at_pct" IS NOT NULL')
        low_income_nodata.setSubsetString('"low_income_lim_at_pct" IS NULL')

        density_renderer = make_graduated_renderer(
            density, "pop_density_calc", "#eff3ff", "#084594", 0
        )
        low_income_renderer = make_graduated_renderer(
            low_income, "low_income_lim_at_pct", "#fff5eb", "#a63603", 1
        )
        density.setRenderer(density_renderer)
        low_income.setRenderer(low_income_renderer)
        density_nodata.setRenderer(make_nodata_renderer())
        low_income_nodata.setRenderer(make_nodata_renderer())
        boundary_density.setRenderer(make_outline_renderer())
        boundary_low_income.setRenderer(make_outline_renderer())
        joined_evidence.setRenderer(make_outline_renderer("#737373", 0.25))

        density.saveNamedStyle(os.path.join(STYLES_DIR, "population_density.qml"))
        density_nodata.saveNamedStyle(os.path.join(STYLES_DIR, "population_density_nodata.qml"))
        low_income.saveNamedStyle(os.path.join(STYLES_DIR, "low_income.qml"))
        low_income_nodata.saveNamedStyle(os.path.join(STYLES_DIR, "low_income_nodata.qml"))
        boundary_density.saveNamedStyle(os.path.join(STYLES_DIR, "toronto_boundary.qml"))

        toronto_csv_uri = (
            "file:///"
            + TORONTO_CSV.replace("\\", "/")
            + "?type=csv&delimiter=,&detectTypes=yes&geomType=none&subsetIndex=no&watchFile=no"
        )
        summary_uri = (
            "file:///"
            + SUMMARY_CSV.replace("\\", "/")
            + "?type=csv&delimiter=,&detectTypes=yes&geomType=none&subsetIndex=no&watchFile=no"
        )
        coverage_uri = (
            "file:///"
            + COVERAGE_CSV.replace("\\", "/")
            + "?type=csv&delimiter=,&detectTypes=yes&geomType=none&subsetIndex=no&watchFile=no"
        )
        toronto_csv_layer = QgsVectorLayer(toronto_csv_uri, "toronto_indicators_2021", "delimitedtext")
        summary_layer = QgsVectorLayer(summary_uri, "stage5_join_summary", "delimitedtext")
        coverage_layer = QgsVectorLayer(coverage_uri, "stage5_indicator_coverage", "delimitedtext")
        if not toronto_csv_layer.isValid() or not summary_layer.isValid() or not coverage_layer.isValid():
            raise RuntimeError("Evidence CSV layer failed to load")

        root = project.layerTreeRoot()
        group_map1 = root.addGroup("Map 1 - Population Density")
        group_map2 = root.addGroup("Map 2 - Low Income")
        group_evidence = root.addGroup("Stage 5 - Join Evidence")

        for layer in (boundary_density, density, density_nodata):
            project.addMapLayer(layer, False)
            group_map1.addLayer(layer)
        for layer in (boundary_low_income, low_income, low_income_nodata):
            project.addMapLayer(layer, False)
            group_map2.addLayer(layer)
        for layer in (joined_evidence, toronto_csv_layer, summary_layer, coverage_layer):
            project.addMapLayer(layer, False)
            group_evidence.addLayer(layer)

        group_map2.setItemVisibilityChecked(False)
        group_evidence.setItemVisibilityChecked(False)

        density_ranges = [
            {"lower": item.lowerValue(), "upper": item.upperValue(), "label": item.label()}
            for item in density.renderer().ranges()
        ]
        low_income_ranges = [
            {"lower": item.lowerValue(), "upper": item.upperValue(), "label": item.label()}
            for item in low_income.renderer().ranges()
        ]

        layout_outputs = []
        layout_outputs.append(
            create_layout(
                project,
                "Map_1_Population_Density",
                "Toronto Population Density by Census Tract",
                "Derived indicator: 2021 population divided by calculated CT area (km²) | 5-class Natural Breaks (Jenks)",
                density,
                density_nodata,
                boundary_density,
                "Indicator year: 2021\nBoundary year: 2021\nUnit: people per km²\nClassification: Natural Breaks (Jenks), 5 classes\nMissing values: grey\n\nSource: Statistics Canada, 2021 Census of Population and 2021 Census Tract Cartographic Boundary File.",
                "toronto_population_density_2021",
            )
        )
        layout_outputs.append(
            create_layout(
                project,
                "Map_2_Low_Income",
                "Toronto Low-Income Prevalence by Census Tract",
                "Low-income status based on LIM-AT (%) | Income reference year 2020 | 5-class Natural Breaks (Jenks)",
                low_income,
                low_income_nodata,
                boundary_low_income,
                "Income reference year: 2020\nCensus product/boundary year: 2021\nUnit: percent\nClassification: Natural Breaks (Jenks), 5 classes\nMissing values: grey\n\nSource: Statistics Canada, 2021 Census Profile and 2021 Census Tract Cartographic Boundary File.",
                "toronto_low_income_2020",
            )
        )

        project.setFileName(PROJECT_PATH)
        if not project.write():
            raise RuntimeError("Failed to write QGIS project")

        summary = {
            "qgis_version": Qgis.QGIS_VERSION,
            "boundary_count": len(boundary_id_set),
            "indicator_count": len(toronto_indicator_ids),
            "matched_count": len(matched_ids),
            "unmatched_boundary_count": len(unmatched_boundaries),
            "unmatched_indicator_count": len(unmatched_indicators),
            "match_rate_pct": match_rate,
            "unmatched_boundary_ids": unmatched_boundaries,
            "unmatched_indicator_ids": unmatched_indicators,
            "coverage": coverage_rows,
            "density_difference": {
                "count": len(density_differences),
                "mean": sum(density_differences) / len(density_differences)
                if density_differences
                else None,
                "max_abs": max(abs(value) for value in density_differences)
                if density_differences
                else None,
            },
            "density_ranges": density_ranges,
            "low_income_ranges": low_income_ranges,
            "outputs": {
                "toronto_csv": TORONTO_CSV,
                "summary_csv": SUMMARY_CSV,
                "coverage_csv": COVERAGE_CSV,
                "gpkg": OUTPUT_GPKG,
                "project": PROJECT_PATH,
                "layouts": layout_outputs,
            },
        }
        with open(SUMMARY_JSON, "w", encoding="utf-8") as handle:
            json.dump(summary, handle, ensure_ascii=False, indent=2)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    finally:
        QgsApplication.exitQgis()


if __name__ == "__main__":
    main()
