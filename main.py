import streamlit as st
from core.graph import graph

final_content = None
answer = None
st.write("### Patrick's RAG Application")
question = st.text_input("What do you want to know about the Ottoman Empire?")
max_loops = st.text_input("How many tries do you want?")

if question:
    if max_loops and int(max_loops) > 0:
        for event in graph.stream({"question": question, "max_loops": int(max_loops)}, stream_mode="values"):
            if event.get('final_answer') is not None:
                answer = str(event.get('final_answer'))

        if 'content=' in answer:
            parts = answer.split('content=')

            if len(parts) > 1:
                content_part = parts[1].split(' additional_kwargs={}')
                
                if len(content_part) > 1:
                    final_content = content_part[0]
                else:
                    print("End pattern '\" additional_kwargs={}' not found.")
            else:
                print("Start pattern 'content=\"' not found.")

            print("Final content is: ", final_content)

        else:
            print("Answer is: ", answer)
    else:
        st.write("Please enter the number of retries...")
else:
    st.write("Please enter your question and the number of retries...")

try: 
    if final_content:
        st.write(final_content)
    elif answer:
        st.write(answer)
    else:
        st.write("")
except Exception as e:
    st.error(f"An error occurred while displaying content: {str(e)}")


