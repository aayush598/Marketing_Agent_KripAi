# app.py (updated)
import streamlit as st
from recommender import TechnologyRecommender
import json
def main():
    st.set_page_config(
        page_title="AI-Powered Technology Stack Recommender",
        page_icon="🤖",
        layout="wide"
    )

    st.title("🤖 AI-Powered Technology Stack Recommender")
    st.markdown("""
    Get customized technology recommendations based on your project requirements, budget, and timeline.
    The system analyzes your project details, selects optimal technologies, assigns the best team, and provides detailed cost estimations.
    """)

    with st.expander("📋 Project Details", expanded=True):
        project_description = st.text_area(
            "Describe your project including key features, expected scale, and team skills...",
            height=200,
            help="Be as detailed as possible about what you're building, who it's for, and any specific requirements"
        )

    col1, col2 = st.columns(2)
    with col1:
        budget_constraint = st.radio(
            "Budget Constraint",
            ["tight", "moderate", "flexible"],
            index=1,
            horizontal=True,
            help="Tight: Minimal viable product, Moderate: Standard features, Flexible: Premium features"
        )
    with col2:
        timeline = st.selectbox(
            "Project Timeline",
            ["1-3 months", "3-6 months", "6-12 months", "12+ months"],
            index=1,
            help="Estimated time to complete the project"
        )

    # Add technology selection checkboxes
    st.subheader("Select Specific Technologies (Optional)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("##### Frontend")
        frontend_react = st.checkbox("React")
        frontend_angular = st.checkbox("Angular")
        frontend_vue = st.checkbox("Vue.js")
        frontend_tailwind = st.checkbox("Tailwind CSS")
    
    with col2:
        st.markdown("##### Backend")
        backend_node = st.checkbox("Node.js")
        backend_python = st.checkbox("Python")
        backend_java = st.checkbox("Java")
        backend_dotnet = st.checkbox(".NET")
    
    with col3:
        st.markdown("##### Database & Infrastructure")
        db_mongo = st.checkbox("MongoDB")
        db_postgres = st.checkbox("PostgreSQL")
        infra_aws = st.checkbox("AWS")
        infra_docker = st.checkbox("Docker/Kubernetes")

    if st.button("Generate Comprehensive Recommendation", type="primary"):
        if not project_description.strip():
            st.error("Please enter a project description")
            return

        # Collect selected technologies
        selected_techs = []
        if frontend_react: selected_techs.append("React")
        if frontend_angular: selected_techs.append("Angular")
        if frontend_vue: selected_techs.append("Vue.js")
        if frontend_tailwind: selected_techs.append("Tailwind")
        if backend_node: selected_techs.append("Node.js")
        if backend_python: selected_techs.append("Python")
        if backend_java: selected_techs.append("Java")
        if backend_dotnet: selected_techs.append("ASP.NET")
        if db_mongo: selected_techs.append("MongoDB")
        if db_postgres: selected_techs.append("PostgreSQL")
        if infra_aws: selected_techs.append("AWS")
        if infra_docker: selected_techs.append("Docker")

        # Update project description with selected technologies if any were chosen
        if selected_techs:
            tech_string = ", ".join(selected_techs)
            project_description += f"\n\nRequired technologies: {tech_string}."

        with st.spinner("Analyzing project, selecting optimal team, and generating detailed recommendations..."):
            recommender = TechnologyRecommender()
            recommendations = recommender.get_structured_recommendations(
                project_description,
                budget_constraint,
                timeline
            )

        st.markdown("## 📊 Technology Stack Recommendation")
        
        # Check if this was a cached result
        if "Cached Project Description" in recommendations:
            st.info("ℹ️ Showing previously generated recommendation from database")
        
        # Display the markdown-formatted recommendations
        st.markdown(recommendations)
        
        # Add a download button for the recommendations
        st.download_button(
            label="Download Recommendations as Markdown",
            data=recommendations,
            file_name="technology_recommendation.md",
            mime="text/markdown"
        )

if __name__ == "__main__":
    main()