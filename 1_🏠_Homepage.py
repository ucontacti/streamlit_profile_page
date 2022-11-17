import streamlit as st


st.set_page_config(
    page_title='Saleh Daghigh | Digital CV',
    layout="centered",
    page_icon='assets/favicon.png'
)
with open('styles/main.css') as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)


with open('assets/Saleh_Daghigh_CV.pdf', "rb") as pdf_file:
    PDFbyte = pdf_file.read()

col1, col2 = st.columns(2, gap="small")
with col1:
    st.image('assets/ProfilePicture.png', width=230)

with col2:
    st.title('Saleh Daghigh')
    st.write('Data Science enthusiast')
    st.download_button(
        label=" 📄 Download Resume",
        data=PDFbyte,
        file_name='Saleh_Daghigh_CV',
        mime="application/octet-stream",
    )
    st.write("📫", 'ucontacti2012@gmail.com')

SOCIAL_MEDIA = {
    "LinkedIn": "https://www.linkedin.com/in/saleh-daghigh/",
    "GitHub": "https://github.com/ucontacti",
    # 'Kaggle': 'https://www.kaggle.com/ucontacti'
}

st.write('\n')
cols = st.columns(len(SOCIAL_MEDIA))
for index, (platform, link) in enumerate(SOCIAL_MEDIA.items()):
    cols[index].write(f"[{platform}]({link})")


st.write('\n')
st.subheader("Hard Skills")
st.write(
    """
- 👩‍💻 Programming: Python, Java, C++
- 🧠 Machine Learning Tools: Tensorflow, Keras, Numpy, Pandas
- 📊 Data Visulization: Streamlit, Matplotlib, Seaborn, Pydeck
- ☁️ Cloud-Based Technologies: Google Cloud Platform, Docker
- 🗄️ Databases: BigQuery, MySQL
"""
)

st.write('\n')
st.subheader("Work History")
st.write("---")

# --- JOB 1
st.write("🚧", "**Software Developer | Tarja GmbH**")
st.write("May 2018 - June 2022")
st.write(
    """
- ► Developed a Java Micro-service to generate Certificate Signing Requests for our clients that facilitated the automation part of certificate generation
- ► Using Python, implemented an API to manage KVM instances
- ► Revised and implemented a Remote Control client (SPICE) using C++, adding custom features to the original client code such as safe tunnel and touch-pad
"""
)

st.write('\n')
st.subheader("Education")
st.write("---")

# --- JOB 1
st.write("🎓", "**Master of Computer Science | University of Bonn**")
st.write("April 2018 - August 2022")
st.write(
    """
- ► Created a fully automated pipeline to fetch new replays, process parsing, and feature creation of different models using the Typer command-line library
- ► Applied state-of-the-art Recurrent Networks, namely LSTM and GRU, reaching 80% AUC and 15% EER
- ► Applied Echo State Network to Itemization features to obtain representations of non-fixed length features, leading to a 95% F1-score and 98% ROC AUC
"""
)

