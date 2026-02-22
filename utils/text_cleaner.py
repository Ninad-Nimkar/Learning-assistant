def clean_text(text: str) -> str:
    #remove line breaks
    text = text.replace("\n", " ")

    #remove stars
    text = text.replace("*", "")

    #remove multiple spaces
    text = " ".join(text.split())

    #llm limit
    if len(text) > 7000:
        text = text[:3000]

    return text