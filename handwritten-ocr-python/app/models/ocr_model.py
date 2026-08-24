AutoModel.from_pretrained(
    "baidu/Unlimited-OCR",
    trust_remote_code=True,
    device_map="auto"
)