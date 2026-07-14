from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET

MAIN_ID = "Population_density__people_per_km___a63bd021_eae5_4eec_96ae_5cae2aa3689d"
NODATA_ID = "No_data_e54fe6f3_1460_4cec_9497_fe3ec7e4a5b7"
OLD_WINDOWS = re.compile(r"C:/Users/86159/Downloads/summer_project-second \(1\)/summer_project-second/stage1_data_cleaning/Toronto_data/processed")


def normalized(source: str, subset: str | None = None) -> str:
    source = OLD_WINDOWS.sub("../Toronto_data/processed", source)
    if subset is not None:
        source = source.split("|subset=", 1)[0] + "|subset=" + subset
    return source


def fix(project_path: Path) -> None:
    with zipfile.ZipFile(project_path) as archive:
        qgs_name = next(name for name in archive.namelist() if name.endswith(".qgs"))
        root = ET.fromstring(archive.read(qgs_name))
        extras = {name: archive.read(name) for name in archive.namelist() if name != qgs_name}

    for element in root.iter():
        source = element.attrib.get("source")
        layer_id = element.attrib.get("id")
        if source:
            if layer_id == MAIN_ID:
                element.set("source", normalized(source, '"population_density_km2" IS NOT NULL'))
            elif layer_id == NODATA_ID:
                element.set("source", normalized(source, '"population_density_km2" IS NULL'))
            else:
                element.set("source", normalized(source))

        destination_source = element.attrib.get("destinationLayerSource")
        if destination_source:
            element.set(
                "destinationLayerSource",
                normalized(destination_source, '"population_density_km2" IS NULL'),
            )

        if element.tag == "lastLayoutExportDir":
            element.text = "../maps"

        if element.tag == "maplayer":
            ident = element.findtext("id")
            datasource = element.find("datasource")
            if datasource is not None and datasource.text:
                if ident == MAIN_ID:
                    datasource.text = normalized(datasource.text, '"population_density_km2" IS NOT NULL')
                elif ident == NODATA_ID:
                    datasource.text = normalized(datasource.text, '"population_density_km2" IS NULL')
                else:
                    datasource.text = normalized(datasource.text)

        if element.tag == "Layer" and element.text:
            if element.text == MAIN_ID:
                element.set("source", normalized(element.attrib.get("source", ""), '"population_density_km2" IS NOT NULL'))
            elif element.text == NODATA_ID:
                element.set("source", normalized(element.attrib.get("source", ""), '"population_density_km2" IS NULL'))
            elif element.attrib.get("source"):
                element.set("source", normalized(element.attrib["source"]))

        label = element.attrib.get("labelText", "")
        if label.startswith("Derived indicator: 2021 population"):
            element.set("labelText", "Statistics Canada reported population density, 2021 | 5-class Natural Breaks (Jenks)")
        if label.startswith("Indicator year: 2021"):
            element.set("labelText", "Indicator year: 2021\nBoundary year: 2021\nUnit: people per km²\nClassification: 5-class Jenks\nMissing values: grey\n\nSource: Statistics Canada\n2021 Census of Population\nand 2021 CT boundary file.")
        if label.startswith("Income reference year: 2020"):
            element.set("labelText", "Income reference year: 2020\nCensus/boundary year: 2021\nUnit: percent\nClassification: 5-class Jenks\nMissing values: grey\n\nSource: Statistics Canada\n2021 Census Profile\nand 2021 CT boundary file.")

    xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    temp = project_path.with_suffix(".fixed.qgz")
    with zipfile.ZipFile(temp, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(qgs_name, xml)
        for name, data in extras.items():
            archive.writestr(name, data)
    temp.replace(project_path)


if __name__ == "__main__":
    import sys
    fix(Path(sys.argv[1]).resolve())
