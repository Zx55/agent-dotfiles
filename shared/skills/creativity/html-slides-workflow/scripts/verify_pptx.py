#!/usr/bin/env python3
"""Validate the static-image PPTX contract using only the Python standard library."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import sys
from typing import Any
from urllib.parse import unquote
import xml.etree.ElementTree as ET
import zipfile

NS: dict[str, str] = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def target_path(owner: str, target: str) -> str:
    target = unquote(target.split("#", 1)[0])
    return posixpath.normpath(target.lstrip("/") if target.startswith("/") else posixpath.join(posixpath.dirname(owner), target))


def relationships(archive: zipfile.ZipFile, owner: str) -> dict[str, tuple[str, str]]:
    part: PurePosixPath = PurePosixPath(owner)
    name: str = str(part.parent / "_rels" / (part.name + ".rels"))
    if name not in archive.namelist():
        return {}
    root: ET.Element = ET.fromstring(archive.read(name))
    return {
        rel.attrib["Id"]: (rel.attrib["Type"].rsplit("/", 1)[-1], target_path(owner, rel.attrib["Target"]))
        for rel in root if rel.attrib.get("TargetMode") != "External"
    }


def note_text(root: ET.Element) -> str:
    bodies: list[ET.Element] = []
    for shape in root.findall(".//p:sp", NS):
        placeholder: ET.Element | None = shape.find("p:nvSpPr/p:nvPr/p:ph", NS)
        if placeholder is not None and placeholder.get("type") == "body":
            body: ET.Element | None = shape.find("p:txBody", NS)
            if body is not None:
                bodies.append(body)
    require(len(bodies) <= 1, "Multiple note body placeholders")
    if not bodies:
        return ""
    paragraphs: list[str] = []
    for paragraph in bodies[0].findall("a:p", NS):
        tokens: list[str] = []
        for element in paragraph.iter():
            if element.tag == f"{{{NS['a']}}}t":
                tokens.append(element.text or "")
            elif element.tag == f"{{{NS['a']}}}br":
                tokens.append("\n")
        paragraphs.append("".join(tokens))
    return "\n".join(paragraphs)


def verify(filename: Path, expected: dict[str, Any]) -> None:
    with zipfile.ZipFile(filename) as archive:
        require(archive.testzip() is None, "Corrupt ZIP member")
        names: list[str] = archive.namelist()
        require(len(names) == len(set(names)), "Duplicate ZIP member")
        for name in names:
            if name.endswith((".xml", ".rels")):
                root: ET.Element = ET.fromstring(archive.read(name))
                if name.endswith(".rels"):
                    rel_path: PurePosixPath = PurePosixPath(name)
                    owner: str = str(rel_path.parent.parent / rel_path.name[:-5]) if name != "_rels/.rels" else ""
                    for rel in root:
                        if rel.attrib.get("TargetMode") != "External":
                            target: str = target_path(owner, rel.attrib["Target"])
                            require(target in names, f"Dangling relationship in {name}: {target}")
        presentation: ET.Element = ET.fromstring(archive.read("ppt/presentation.xml"))
        size: ET.Element | None = presentation.find("p:sldSz", NS)
        require(size is not None, "Missing slide size")
        assert size is not None
        width: int = round(expected["canvas"]["width"] * 9525)
        height: int = round(expected["canvas"]["height"] * 9525)
        require(abs(int(size.attrib["cx"]) - width) <= 1 and abs(int(size.attrib["cy"]) - height) <= 1, "Wrong slide dimensions")
        identifiers: list[ET.Element] = presentation.findall("p:sldIdLst/p:sldId", NS)
        require(len(identifiers) == len(expected["slides"]), "Wrong slide count")
        presentation_rels: dict[str, tuple[str, str]] = relationships(archive, "ppt/presentation.xml")
        for identifier, entry in zip(identifiers, expected["slides"]):
            kind, slide_path = presentation_rels[identifier.attrib[f"{{{NS['r']}}}id"]]
            require(kind == "slide", "Wrong presentation relationship type")
            slide: ET.Element = ET.fromstring(archive.read(slide_path))
            pictures: list[ET.Element] = slide.findall("p:cSld/p:spTree/p:pic", NS)
            require(len(pictures) == 1, f"{entry['name']}: expected one full-slide picture")
            picture: ET.Element = pictures[0]
            offset: ET.Element | None = picture.find("p:spPr/a:xfrm/a:off", NS)
            extent: ET.Element | None = picture.find("p:spPr/a:xfrm/a:ext", NS)
            require(offset is not None and extent is not None, "Missing image geometry")
            assert offset is not None and extent is not None
            require(int(offset.attrib["x"]) == 0 and int(offset.attrib["y"]) == 0, "Image not at origin")
            require(abs(int(extent.attrib["cx"]) - width) <= 1 and abs(int(extent.attrib["cy"]) - height) <= 1, "Image does not fill slide")
            blip: ET.Element | None = picture.find("p:blipFill/a:blip", NS)
            require(blip is not None, "Missing image reference")
            assert blip is not None
            rels: dict[str, tuple[str, str]] = relationships(archive, slide_path)
            _, image_path = rels[blip.attrib[f"{{{NS['r']}}}embed"]]
            require(hashlib.sha256(archive.read(image_path)).hexdigest() == entry["imageHash"], "Embedded image differs or slides were reordered")
            note_paths: list[str] = [target for kind, target in rels.values() if kind == "notesSlide"]
            require(len(note_paths) <= 1, "Multiple note relationships")
            actual: str = note_text(ET.fromstring(archive.read(note_paths[0]))) if note_paths else ""
            require(actual == entry["notes"], f"{entry['name']}: speaker notes differ from the full source text")
    print(f"OOXML OK: {len(expected['slides'])} slides, image geometry/order, relationships, and complete notes")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: verify_pptx.py candidate.pptx expected.json")
    try:
        verify(Path(sys.argv[1]), json.loads(Path(sys.argv[2]).read_text(encoding="utf-8")))
    except (OSError, ValueError, KeyError, ET.ParseError, zipfile.BadZipFile) as error:
        raise SystemExit(f"PPTX verification failed: {error}") from error


if __name__ == "__main__":
    main()
