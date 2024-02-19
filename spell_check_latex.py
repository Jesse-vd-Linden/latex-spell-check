import os
import glob
import shutil
from pathlib import Path
from openai import OpenAI
from datetime import datetime
from tqdm import tqdm

client = OpenAI()

def evident_spelling_mistakes(text):
    system_prompt = "You are a proof reader of a thesis."\
        "Your goal is to find all the evident mistakes in the supplied text. Point out all the incorrect things that are just sloppy writing" \
        "Look at spelling mistakes, sentences that do not make sense and claims or things that just seem incorrect" \
        "Point out the texts that are incorrect and what is incorrect. Do no give tips in how to improve them." \
        "Be extremely harsh and nitpick as much as you can"
        
    user_prompt = f"Spelling check this text:\n{text}"
    completion = client.chat.completions.create(
        model="gpt-4",
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return completion.choices[0].message.content

def restructuring_sentences(chapter, title, text):
    system_prompt = "You are a proof reader for a thesis." \
        "Your goal is to look at the current writing of sentences and paragraphs and give tips on how to improve the reading flow of these sentences and paragraphs" \
        "For sentences give clear examples of how to improve the sentences." \
        "For paragraphs give reasons why the current writing and structure is not good." 
        
    user_prompt = f"Spelling check this section in the {chapter} with the section title {title}:\ntext:{text}"
    completion = client.chat.completions.create(
        model="gpt-4",
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return completion.choices[0].message.content

def general_writing_tips(chapter, title, text):
    system_prompt = "You are a writing coach for acadamic writers." \
        "Look at the follow text which is one section of a thesis and give clear instructions on how to improve the writing of this student." \
        "Give tips on the scientific manner of the writing, such as if decisions or claims are substantiated" \
        "And does the specific section"
        
    user_prompt = f"Spelling check this section in the {chapter} with the section title {title}:\ntext:{text}"
    completion = client.chat.completions.create(
        model="gpt-4",
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return completion.choices[0].message.content


if __name__ == "__main__":
    folder = "files/doc"
    # Define the directory
    directory = Path(folder)

    # Find all files with .txt extension recursively
    latex_files = directory.rglob('*.tex')
    
    blocked_files = [
        "report.tex",
        "appendix-e.tex",
        "appendix-X.tex",
        "old-discussion.tex",
    ]
    filtered_files = []
    
    # Find all Markdown files in the source directory
    markdown_files = glob.glob(os.path.join("", '*.md'))
    destination_directory = 'old_results'
    os.makedirs(destination_directory, exist_ok=True)
    for file_path in markdown_files:
        print(file_path)
        if "README" in file_path:
            print("Skipping")
            continue
        destination_file_path = os.path.join(destination_directory, os.path.basename(file_path))
        shutil.move(file_path, destination_file_path)
    
    time = datetime.now().strftime("%Y%m%d_%H%M%S")
    markdown_filename = f"spelling_check_{time}.md"
    with open(markdown_filename, 'w', encoding='utf-8') as file:
        file.write('# Latex Spelling Check\n\n')
    
    for latex_file in tqdm(latex_files):
        if str(latex_file).split("\\")[-1] in blocked_files:
            continue
        
        with open(latex_file, 'r', encoding='utf-8') as file:
            tex_content = file.read()
        
        sections = tex_content.split("\section{")
        chapter = str(latex_file).split("\\")[-1].split(".")[0]
        first_section = True
        
        for section in sections:
            if first_section:
                title = chapter
                text = section
                first_section = False
            else:
                title = section.split("}")[0]
                text = "}".join(section.split("}")[1:])
            
            evident_mistakes = evident_spelling_mistakes(text)
            sentence_restructure = restructuring_sentences(chapter, title, text)
            writing_tips = general_writing_tips(chapter, title, text)
            with open(markdown_filename, 'a', encoding='utf-8') as markdown_file:
                markdown_file.write(f'## {title}\n\n')
                
                markdown_file.write(f'### Evident mistakes\n')
                markdown_file.write(evident_mistakes)
                markdown_file.write("\n\n")
                
                markdown_file.write(f'### Text restructuring\n')
                markdown_file.write(sentence_restructure)
                markdown_file.write("\n\n")
            
                markdown_file.write(f'### Writing tips\n')
                markdown_file.write(writing_tips)
                markdown_file.write("\n\n")
                
            break
        break
            
        
