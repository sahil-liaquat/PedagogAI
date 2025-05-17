import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LessonRequest(BaseModel):
    content_type: str 
    subject: str
    grade_level: str
    topic: str
    duration: int
    curriculum_standards: str
    student_needs: str
    pedagogical_preferences: str
    additional_information: str = ""
     

llm = OpenAI(temperature=0.7,max_tokens=1500, openai_api_key=os.getenv("OPENAI_API_KEY"))


lesson_prompt_template = PromptTemplate(
    input_variables=[
        "subject", 
        "grade_level", 
        "topic", 
        "duration", 
        "curriculum_standards", 
        "student_needs", 
        "pedagogical_preferences", 
        "additional_information"
    ],
    template=(
        "Generate learning objectives for a {subject} lesson on '{topic}' for {grade_level} students that align with {curriculum_standards}. "
        "Ensure the objectives include opportunities for student choice and peer discussion. For example, students should design inquiry projects, collaborate, or present their findings to peers for feedback.\n\n"
        
        "Now, design a {duration}-minute lesson for '{topic}' where students:\n"
        "1. Set personal learning goals (e.g., 'I want to understand how X affects Y').\n"
        "2. Choose between 3 activity options (e.g., research, experiment, creative storytelling).\n"
        "3. Self-assess their work using a rubric they co-create.\n\n"
        
        "The activities should include:\n"
        "Option 1: [Example Activity 1]\n"
        "Option 2: [Example Activity 2]\n"
        "Option 3: [Example Activity 3]\n\n"
        
        "Next, generate discussion prompts that:\n"
        "1. Start with student-generated questions (e.g., 'What surprised you about this topic?').\n"
        "2. Include peer-to-peer feedback loops (e.g., 'Swap drafts and suggest one improvement').\n"
        "3. Use open-ended questions (e.g., 'How might this change if we altered X?').\n\n"
        
        "For the classroom dialogue, consider strategies like Think-Pair-Share, Fishbowl Debate, or Peer Review Stations.\n\n"
        
        "Finally, integrate a reflection activity where students:\n"
        "1. Rate their confidence in the topic pre/post-lesson.\n"
        "2. Write one thing they’d change about their approach.\n"
        "3. Suggest a real-world application of what they learned.\n\n"
        
        "Ensure that the lesson minimizes teacher-led activities, maximizes student agency, and includes at least two opportunities for peer collaboration. Avoid worksheets or quizzes as primary assessments.\n\n"
        
        "Use the following structure for the lesson plan:\n"
        "**Learning Objectives**:\n"
        "**Materials**:\n"
        "**Warm-Up**:\n"
        "**Main Activity**:\n"
        "**Assessment**:\n"
        "**Conclusion**:\n\n"
        "Align with: {curriculum_standards}\n"
        "Address: {student_needs}\n"
        "Use: {pedagogical_preferences}\n"
        "Notes: {additional_information}"
   )
)

quiz_prompt_template = PromptTemplate(
    input_variables=[
        "subject", 
        "grade_level", 
        "topic", 
    
    ],
    template=(
        "Generate a **quiz** for a {subject} lesson on '{topic}' for {grade_level} students. "
        "The quiz should test students' understanding of key concepts and provide varied question formats (multiple choice, short answer, true/false).\n\n"
        "**Questions**:\n"
        "1. [Sample Question 1]\n"
        "2. [Sample Question 2]\n"
        "3. [Sample Question 3]\n\n"
    
    )
)

study_guide_prompt_template = PromptTemplate(
    input_variables=[
        "subject", 
        "grade_level", 
        "topic", 
        "curriculum_standards", 
        "student_needs", 
        "additional_information"
    ],
    template=(
        "Generate a **study guide** for a {subject} lesson on '{topic}' for {grade_level} students that aligns with {curriculum_standards}. "
        "The study guide should provide summaries of key concepts, practice questions, and resources for further study.\n\n"
        "**Key Concepts**:\n"
        "1. [Concept 1]\n"
        "2. [Concept 2]\n"
        "3. [Concept 3]\n\n"
        "**Practice Questions**:\n"
        "1. [Practice Question 1]\n"
        "2. [Practice Question 2]\n"
        "3. [Practice Question 3]\n\n"
        "Include student needs considerations: {student_needs}\n"
        "Notes: {additional_information}"
    )
)

@app.post("/generate_content/")
async def generate_content(data: LessonRequest):
    if data.content_type == "lesson_plan":
        prompt = lesson_prompt_template.format(
            subject=data.subject,
            grade_level=data.grade_level,
            topic=data.topic,
            duration=data.duration,
            curriculum_standards=data.curriculum_standards,
            student_needs=data.student_needs,
            pedagogical_preferences=data.pedagogical_preferences,
            additional_information=data.additional_information
        )
    elif data.content_type == "quiz":
        prompt = quiz_prompt_template.format(
            subject=data.subject,
            grade_level=data.grade_level,
            topic=data.topic,
            curriculum_standards=data.curriculum_standards,
            student_needs=data.student_needs,
            additional_information=data.additional_information
        )
    elif data.content_type == "study_guide":
        prompt = study_guide_prompt_template.format(
            subject=data.subject,
            grade_level=data.grade_level,
            topic=data.topic,
            curriculum_standards=data.curriculum_standards,
            student_needs=data.student_needs,
            additional_information=data.additional_information
        )
    else:
        return {"error": "Invalid content type. Please choose 'lesson_plan', 'quiz', or 'study_guide'."}
    
    response = llm(prompt)
    return {f"{data.content_type}": response} 
