from flask import Flask, render_template, request
import os
import openai
from metaphor_python import Metaphor
openai.api_key = os.getenv("OPENAI_API_KEY")

metaphor = Metaphor(os.getenv("METAPHOR_API_KEY"))

app = Flask(__name__)

@app.route('/')
@app.route("/home")
def home():
    return render_template('landing.html')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        university_name = request.form['university_name']
        department_of_study = request.form['department_of_study']
        research_interests = request.form['research_interests']
        
        USER_QUESTION = f"{department_of_study} Department at {university_name}"

        SYSTEM_MESSAGE = "You are a helpful assistant that generates search queiries based on user questions. Only generate one search query."

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": USER_QUESTION},
            ],
        )


        query = completion.choices[0].message.content
        search_response = metaphor.search(
            query, use_autoprompt=True
        )
        print(f"URLs: {[result.url for result in search_response.results]}\n")

        contents_result = search_response.get_contents()
        first_result = contents_result.contents[0]

        SYSTEM_MESSAGE = f"You are a helpful assistant that would tell me the names of atleast five {department_of_study} professors researching on {research_interests} at {university_name} based on extracted data "

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": first_result.extract},
            ],
        )

        prof_names = completion.choices[0].message.content
        print(f" {prof_names}")
        return render_template('result.html', prof_names=prof_names,university_name=university_name, department_of_study=department_of_study,research_interests=research_interests)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
