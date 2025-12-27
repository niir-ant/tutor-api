"""
Manage Subjects Page
"""
import streamlit as st
from ui.utils.api_client import get_api_client


def render():
    """Render subject management page"""
    st.title("📚 Manage Subjects")
    
    api_client = get_api_client()
    
    tab1, tab2, tab3 = st.tabs(["List Subjects", "Create Subject", "Edit Subject"])
    
    with tab1:
        st.subheader("All Subjects")
        
        status_filter = st.selectbox("Filter by Status", ["all", "active", "inactive"])
        
        with st.spinner("Loading subjects..."):
            subjects_data = api_client.list_subjects(
                status=status_filter if status_filter != "all" else None
            )
        
        if subjects_data and "subjects" in subjects_data:
            subjects = subjects_data["subjects"]
            st.write(f"Found {len(subjects)} subject(s)")
            
            for subject in subjects:
                with st.expander(f"{subject.get('name')} ({subject.get('subject_code')})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Type:** {subject.get('type', 'N/A')}")
                        st.write(f"**Status:** {subject.get('status', 'N/A')}")
                        grade_levels = subject.get("grade_levels", [])
                        if grade_levels:
                            st.write(f"**Grade Levels:** {', '.join(map(str, grade_levels))}")
                        else:
                            st.write("**Grade Levels:** All levels")
                    with col2:
                        st.write(f"**Question Types:** {', '.join(subject.get('supported_question_types', []))}")
                        st.write(f"**Validation Method:** {subject.get('answer_validation_method', 'N/A')}")
                    
                    # Show description if available
                    description = subject.get('description')
                    if description:
                        st.write(f"**Description:** {description}")
                    
                    # Show metadata if available (need to fetch full details)
                    subject_id = subject.get('subject_id')
                    if subject_id:
                        try:
                            subject_detail = api_client.get_subject(str(subject_id))
                            if subject_detail and not subject_detail.get("error"):
                                metadata = subject_detail.get("metadata")
                                if metadata:
                                    st.markdown("---")
                                    st.write("**Metadata:**")
                                    metadata_col1, metadata_col2 = st.columns(2)
                                    with metadata_col1:
                                        if metadata.get("curriculum"):
                                            st.write(f"**Curriculum:** {metadata.get('curriculum')}")
                                        if metadata.get("category"):
                                            st.write(f"**Category:** {metadata.get('category')}")
                                    with metadata_col2:
                                        if metadata.get("icon_url"):
                                            st.write(f"**Icon URL:** {metadata.get('icon_url')}")
                                    learning_objectives = metadata.get("learning_objectives")
                                    if learning_objectives:
                                        st.write("**Learning Objectives:**")
                                        for obj in learning_objectives:
                                            st.write(f"- {obj}")
                        except:
                            pass  # Silently fail if can't fetch details
        else:
            st.info("No subjects found.")
    
    with tab2:
        st.subheader("Create New Subject")
        
        with st.form("create_subject_form"):
            st.write("**Basic Information**")
            subject_code = st.text_input("Subject Code (unique identifier)", help="e.g., 'chemistry', 'history'")
            name = st.text_input("Subject Name", help="Display name for the subject")
            description = st.text_area("Description", help="Optional description of the subject")
            subject_type = st.selectbox("Type", ["academic", "programming", "language", "science", "other"])
            
            st.markdown("---")
            st.write("**Configuration**")
            grade_levels = st.multiselect("Grade Levels (leave empty for all)", list(range(6, 13)), help="Select specific grade levels or leave empty for all levels")
            
            question_types = st.multiselect(
                "Supported Question Types",
                ["multiple_choice", "short_answer", "code_completion", "code_writing", "fill_blank", "true_false"],
                help="Select which question types are supported for this subject"
            )
            
            validation_method = st.selectbox(
                "Answer Validation Method",
                ["ai_semantic", "code_execution", "exact_match", "ai_structured"],
                help="Method used to validate student answers"
            )
            
            st.markdown("---")
            st.write("**Metadata (Optional)**")
            with st.expander("Subject Metadata", expanded=False):
                curriculum = st.text_input("Curriculum Alignment", help="e.g., 'Common Core', 'State Standards'")
                category = st.text_input("Category", help="Subject category or tag")
                icon_url = st.text_input("Icon URL", help="URL to subject icon/image")
                
                st.write("**Learning Objectives**")
                learning_objectives_input = st.text_area(
                    "Learning Objectives (one per line)",
                    help="Enter learning objectives, one per line"
                )
            
            if st.form_submit_button("Create Subject", use_container_width=True, type="primary"):
                # Validation
                if not subject_code or not name:
                    st.error("❌ Subject Code and Name are required")
                elif not question_types:
                    st.error("❌ At least one question type must be selected")
                elif not validation_method:
                    st.error("❌ Validation method is required")
                else:
                    # Prepare metadata
                    metadata = None
                    if curriculum or category or icon_url or learning_objectives_input:
                        metadata = {}
                        if curriculum:
                            metadata["curriculum"] = curriculum
                        if category:
                            metadata["category"] = category
                        if icon_url:
                            metadata["icon_url"] = icon_url
                        if learning_objectives_input:
                            # Split by newlines and filter empty lines
                            objectives = [obj.strip() for obj in learning_objectives_input.split("\n") if obj.strip()]
                            if objectives:
                                metadata["learning_objectives"] = objectives
                    
                    # Prepare grade levels (empty list means None/all levels)
                    grade_levels_to_send = grade_levels if grade_levels else None
                    
                    with st.spinner("Creating subject..."):
                        result = api_client.create_subject(
                            subject_code=subject_code,
                            name=name,
                            description=description if description else None,
                            type=subject_type,
                            grade_levels=grade_levels_to_send,
                            supported_question_types=question_types,
                            answer_validation_method=validation_method,
                            settings=None,  # Can be added later
                            metadata=metadata,
                        )
                    
                    if result and not result.get("error"):
                        st.success(f"✅ Subject '{name}' created successfully!")
                        st.balloons()
                        # Clear form by rerunning
                        st.rerun()
                    else:
                        error_msg = result.get("detail", "Failed to create subject") if result else "Failed to create subject"
                        st.error(f"❌ {error_msg}")
    
    with tab3:
        st.subheader("Edit Subject")
        
        # Get list of subjects for selection
        with st.spinner("Loading subjects..."):
            subjects_data = api_client.list_subjects()
        
        if subjects_data and "subjects" in subjects_data and len(subjects_data["subjects"]) > 0:
            subjects = subjects_data["subjects"]
            subject_options = {f"{s.get('name')} ({s.get('subject_code')})": s.get('subject_id') for s in subjects}
            
            selected_subject_name = st.selectbox("Select Subject to Edit", list(subject_options.keys()))
            selected_subject_id = subject_options.get(selected_subject_name)
            
            if selected_subject_id:
                # Fetch subject details
                with st.spinner("Loading subject details..."):
                    subject_detail = api_client.get_subject(str(selected_subject_id))
                
                if subject_detail and not subject_detail.get("error"):
                    with st.form("edit_subject_form"):
                        st.write("**Basic Information**")
                        name = st.text_input("Subject Name", value=subject_detail.get('name', ''))
                        description = st.text_area("Description", value=subject_detail.get('description', ''))
                        
                        st.markdown("---")
                        st.write("**Configuration**")
                        current_grade_levels = subject_detail.get("grade_levels", [])
                        grade_levels = st.multiselect(
                            "Grade Levels (leave empty for all)",
                            list(range(6, 13)),
                            default=current_grade_levels if current_grade_levels else []
                        )
                        
                        current_question_types = subject_detail.get("supported_question_types", [])
                        question_types = st.multiselect(
                            "Supported Question Types",
                            ["multiple_choice", "short_answer", "code_completion", "code_writing", "fill_blank", "true_false"],
                            default=current_question_types
                        )
                        
                        current_status = subject_detail.get("status", "active")
                        status = st.selectbox("Status", ["active", "inactive", "archived"], index=["active", "inactive", "archived"].index(current_status) if current_status in ["active", "inactive", "archived"] else 0)
                        
                        st.markdown("---")
                        st.write("**Metadata**")
                        metadata = subject_detail.get("metadata", {}) or {}
                        
                        curriculum = st.text_input("Curriculum Alignment", value=metadata.get("curriculum", ""))
                        category = st.text_input("Category", value=metadata.get("category", ""))
                        icon_url = st.text_input("Icon URL", value=metadata.get("icon_url", ""))
                        
                        st.write("**Learning Objectives**")
                        current_objectives = metadata.get("learning_objectives", [])
                        learning_objectives_input = st.text_area(
                            "Learning Objectives (one per line)",
                            value="\n".join(current_objectives) if current_objectives else ""
                        )
                        
                        if st.form_submit_button("Update Subject", use_container_width=True, type="primary"):
                            # Prepare metadata
                            updated_metadata = {}
                            if curriculum:
                                updated_metadata["curriculum"] = curriculum
                            if category:
                                updated_metadata["category"] = category
                            if icon_url:
                                updated_metadata["icon_url"] = icon_url
                            if learning_objectives_input:
                                objectives = [obj.strip() for obj in learning_objectives_input.split("\n") if obj.strip()]
                                if objectives:
                                    updated_metadata["learning_objectives"] = objectives
                            
                            # If no metadata fields are filled, set to empty dict to clear existing metadata
                            if not updated_metadata:
                                updated_metadata = {}
                            
                            # Prepare grade levels
                            grade_levels_to_send = grade_levels if grade_levels else None
                            
                            with st.spinner("Updating subject..."):
                                result = api_client.update_subject(
                                    subject_id=str(selected_subject_id),
                                    name=name,
                                    description=description if description else None,
                                    grade_levels=grade_levels_to_send,
                                    status=status,
                                    supported_question_types=question_types,
                                    settings=None,  # Can be added later
                                    metadata=updated_metadata if updated_metadata else None,
                                )
                            
                            if result and not result.get("error"):
                                st.success(f"✅ Subject '{name}' updated successfully!")
                                st.rerun()
                            else:
                                error_msg = result.get("detail", "Failed to update subject") if result else "Failed to update subject"
                                st.error(f"❌ {error_msg}")
                else:
                    st.error("❌ Could not load subject details")
        else:
            st.info("No subjects available to edit.")
