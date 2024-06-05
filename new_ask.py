import os
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import re
from helper_max import *
import subprocess
from helper_marian import *


# Main function to run the program
def main():
    #Known Code
    check_openai_api_key()
    
    # Initialize components
    vectordb = initialize_vector_db()
    retriever = setup_retriever(vectordb)
    llm = initialize_llm()
    qa_chain = create_qa_chain(llm, retriever)
    
    user_query = "I want to learn the physics of ackermann steering"
    
    # Refine query with GPT-4 (assuming this function is defined elsewhere)
    refined_query = refine_query_with_gpt4o(llm, user_query)
    print(refined_query)
    
    # Process refined query
    answer, source_docs = process_query(qa_chain, refined_query + "\ndo not split your python code into multiple segments. \
                                        Give the entire python file instead. \
                                        Do not include a main function. \
                                        Position the text in a meaningful relation to the animation. \
                                        Pay attention so that objects dont overlap each other, when new stuff is added. \
                                        Delete old elements when new stuff is plotted \
                                        Make sure to not render objects outside of the screen.\
                                        Avoid any wait instructions.")
    print("Response:", answer)
    
    # Extract the longest Python code block
    longest_python_code = extract_longest_python_code(answer)

    #print("Source Documents:")
    #for doc in source_docs:
    #    print(doc.metadata["source"])






    ###### CHANGES MARIAN
    custom_media_dir = 'custom_media' #Clear Old Output Directory 
    if os.path.exists(custom_media_dir):
        shutil.rmtree(custom_media_dir)

    if longest_python_code:        
        # Save and run the extracted code block
        print("Python code found in the response.")
        success, error_message = save_and_run_extracted_code(longest_python_code) #Automatic Code Execution
        

        if not success: #Could be used for automatic error correction (Was very important previously to the embedding)
            prompt = f"The following code resulted in an error:\n{longest_python_code}\nError message:\n{error_message}\nPlease provide the correct code."
            #print(prompt)  # Or handle the refined prompt in another way
            print("Error in Code!")
        else:
            # Extract and process images if the code runs successfully
            base64_image = extract_and_process_images() #Extracts Slideshow from Animation
    else:
        print("No Python code found in the response.")


    # Passes the slideshow image to GPT for evaluation (uses the openai gpt query instead of langchain because image might not be supported for langchain yet)
    follow_up_prompt = f"Here is the image slideshow of the animated video. Critically evaluate if this video answers the users question sufficiently: \n{user_query}\n \
    Make sure to criticize if any text appears cropped, cut or covered"
    feedback = get_code_from_openai(follow_up_prompt, base64_image)
    print(feedback)

if __name__ == "__main__":
    main()