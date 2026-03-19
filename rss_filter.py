import requests
from lxml import etree

SOURCE_RSS = "https://www.spreaker.com/show/6846358/episodes/feed"
OUTPUT_FILE = "rss-science.xml"
SCIENCE_TAG = "science"

# namespace correcto de itunes
ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"


def main():
    response = requests.get(SOURCE_RSS)
    response.raise_for_status()

    root = etree.fromstring(response.content)
    channel = root.find("channel")
    items = channel.findall("item")

    selected_items = []

    for item in items:
        title = item.findtext("title")

        # ESTA es la línea clave (namespace correcto)
        keywords_el = item.find(f"{{{ITUNES_NS}}}keywords")

        if keywords_el is not None and keywords_el.text:
            tags = [k.strip().lower() for k in keywords_el.text.split(",")]
        else:
            tags = []

        print(title, "=>", tags)

        if SCIENCE_TAG in tags:
            selected_items.append(item)

    # borrar todos los items
    for item in items:
        channel.remove(item)

    # añadir solo los de ciencia
    for item in selected_items:
        channel.append(item)

    # ajustar título del feed
    title_el = channel.find("title")
    if title_el is not None:
        title_el.text = title_el.text + " - Science"

    # guardar archivo
    with open(OUTPUT_FILE, "wb") as f:
        f.write(
            etree.tostring(
                root,
                xml_declaration=True,
                encoding="UTF-8",
                pretty_print=True
            )
        )

    print(f"\nListo. Se generó {OUTPUT_FILE} con {len(selected_items)} episodios.\n")


if __name__ == "__main__":
    main()
