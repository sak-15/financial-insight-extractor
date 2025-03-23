from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "mistralai/Mistral-7B-Instruct"
local_path = "Users/sakshiii/Desktop/financial-insight-extractor/mistral"  

print("Downloading the model...")
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

print("Saving the model locally...")
model.save_pretrained(local_path)
tokenizer.save_pretrained(local_path)

print("Model downloaded and saved successfully!")
