import sys, re

def rewrite_entry(entry):
    # Extracting the relevant portions
    metadata_match = re.search(r'(?=(# METADATA: .+))', entry)
    # print(metadata_match.groups())
    metadata_text = metadata_match.group(1).strip() if metadata_match else "" 

    text_match = re.search(r'# METADATA: .+?\n(.+?)Q:', entry, re.DOTALL)
    text_before_question = text_match.group(1).strip() if text_match else ""

    question_match = re.search(r'Q: (.+?)\nA:', entry, re.DOTALL)
    question_text = question_match.group(1) if question_match else ""

    answer_match = re.search(r'\nA: (.+)', entry)
    answer_text = answer_match.group(1) if answer_match else ""

    # Constructing the rewritten entry
    # rewritten_entry = f"{metadata_text}\nBob said, \"{text_before_question}\"\n\nQ: {question_text.rstrip('?')} in Bob’s opinion?\nA: {answer_text}"
    # rewritten_entry = f"{metadata_text}\n{text_before_question}\n\nQ: {question_text.rstrip('?')} based on the given text?\nA: {answer_text}"
    # rewritten_entry = f"{metadata_text}\nInstruction: read the given information and answer the corresponding question\n{text_before_question}\n\nQ: {question_text}\nA: {answer_text}"
    # rewritten_entry = f"{metadata_text}\nInstruction: read a piece of text and then use the information in the text to answer a question\n{text_before_question}\n\nQ: {question_text}\nA: {answer_text}"
    rewritten_entry = f"{metadata_text}\nInstruction: read the given information and answer the questions that follow\n{text_before_question}\n\nQ: {question_text}\nA: {answer_text}"

    return rewritten_entry

def main(input_file_name):
    # Reading the input file
    with open(input_file_name, "r") as file:
        entries = file.read()

    # Splitting the entries
    entries = re.split(r'(?=# METADATA: \{"qid": "[\w-]+"\})', entries)
    # print(entries)
    # print(len(entries))

    # Rewriting the entries
    rewritten_entries = [rewrite_entry(entry) for entry in entries[1:]]

    # Writing the rewritten entries to a new file
    output_file_name = input_file_name
    with open(output_file_name, "w") as file:
        for entry in rewritten_entries:
            file.write(entry + "\n\n\n")
    print(f"Rewritten entries saved to {output_file_name}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py input_file_name.txt")
    else:
        input_file_name = sys.argv[1]
        main(input_file_name)
