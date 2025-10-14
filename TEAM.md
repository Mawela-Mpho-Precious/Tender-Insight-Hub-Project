# Team Leadership Log

## Week 1 Team Lead Report
**Lead:** Mawela Mpho Precious  
**Responsibilities:** Initial project setup, repo structure, Git setup  
**Decisions Made:** Chose FastAPI, defined team roles

## Week 2 Team Lead Report  
**Lead:** Mawela Mpho Precious  

### Responsibilities / Decisions Made
This week, we successfully implemented data extraction from the **Tender Insight Keyword Search, Filtering & Match Ranking** feature. Key achievements include:

- Users can enter free-text keywords (e.g., “road construction”, “security services”) into a search bar.  
- The backend performs a search on tender descriptions retrieved from the **OCDS eTenders API**.  
- Search results can be filtered by:  
  - Province  
  - Buyer (organ of state)  
- Users apply filters after receiving the initial search results to narrow down the tenders.  
- Once filters are applied, users can view the tenders that match their criteria.  

### Key Decisions Made
- We decided to divide parts of the work among team members to improve efficiency and ensure each feature could be developed in parallel.  

### Challenges Faced and Solutions
- Initially, the API was not extracting data correctly, which blocked progress. After troubleshooting, we resolved the issue, and the API is now fully functional.  
- Filtering by **submission deadline window** and **budget range** was not possible at first. While full filtering is still under refinement, we implemented partial filters (province and buyer) to ensure progress.  

### Reflections on Teamwork and Leadership
- Dividing tasks allowed the team to work efficiently and made collaboration smoother.  
- Leading the team taught me the importance of clear communication and quickly addressing blockers to keep progress on track.  
- Working through the API issues together reinforced the value of persistence and problem-solving in a team setting.  
# Team Leadership Log

## Week 3 Team Lead Report
**Lead:** Kelebogile Dlamini

### Responsibilities / Decisions Made
This week, our focus was on the **Company Profile Management** feature and finalizing the **Tender Document Summarization** process.

- Worked on the Company Profile schema and discussed its required fields (industry sector, services, certifications, geographic coverage, years of experience, contact information).  
- Decided that each team member should attempt to work on the Company Profile individually and present their solution during the next meeting to move forward.  
- Completed the AI summarization feature:  
  - Implemented text extraction for PDF and ZIP tender documents.  
  - Integrated a HuggingFace transformer model to generate summaries emphasizing objectives, scope, deadlines, and eligibility criteria.  
  - Successfully tested the summarization pipeline with sample documents.

### Key Decisions Made
- Chose MongoDB as the NoSQL database for storing tender text and summaries.  
- Finalized the first iteration of the summarization pipeline and approved it for integration.  
- Adopted a collaborative approach to Company Profile development by having all team members contribute individually.

### Challenges Faced and Solutions
- The Company Profile feature is still incomplete, which slowed progress. To solve this, everyone will work on their own version and merge ideas next week.  
- Some tender PDFs had extraction issues, which were resolved by testing and selecting the most reliable PDF processing library.

### Reflections on Teamwork and Leadership
- Having all members contribute to the Company Profile feature encourages creativity and will help us find the best approach.  
- Completing the AI summarization feature boosted team confidence and gave us a sense of progress.  
- This week required me to motivate the team and make sure we stay focused despite the challenges with the profile feature.

### Week 4 Goals
- Merge individual contributions for the **Company Profile Management** feature and finalize backend implementation.  
- Connect FastAPI endpoints for Company Profile with PostgreSQL and MongoDB.  
- Begin integrating AI summarization into the main tender workflow for end-to-end testing.  
- Continue testing keyword search and filtering features with real tender data.  
- Prepare documentation for all implemented features to ensure smooth knowledge transfer and team alignment.

### Week 4 Team Lead Report  

**Lead:** Ayanda Girly Khalo  

---

### Key Decisions Made During Leadership  
- During this week’s team meetup, we received valuable insights from our supervisor regarding the AI summarization feature. Based on this feedback, I led the decision to integrate the summarization function with the search button. This allows the system to summarize all PDFs associated with a search query, ensuring that the summarization tool is practical and directly connected to user actions.  

### Challenges Faced and How They Were Addressed  
- One of the major challenges we encountered was retrieving documents from the API and correctly matching them with the relevant tender. This issue initially slowed down our progress, as it was critical to ensure that the summarization applied to the correct documents.  
- To address this, the team collaborated to refine our API calls and implement checks that improved document retrieval accuracy. Through iterative testing and adjustments, we managed to align the retrieved documents with the intended tenders.  

### Reflections on Teamwork and Leadership  
- This week’s experience reinforced the importance of teamwork and adaptability. As a team, we were open to guidance from our supervisor and used it constructively to refine our approach.  
- I learned that effective leadership is not only about making decisions but also about ensuring that the team stays focused on solving challenges collectively. Guiding the team through the API retrieval challenge also highlighted the importance of patience, communication, and encouraging problem-solving collaboration.  

### Week 5 Team Lead Report  

*Lead:* Hope Lerato Nkoana  

---

### Key Decisions Made During Leadership  
- During this week, the team focused on refining the AI Summarization feature to link it with the match tender functionality. This improvement aimed to make the summarization more accurate and directly connected to the tender matching process.  

### Challenges Faced and How They Were Addressed  
- A major challenge was that the match tender functionality was not linked with the company profiles, which affected the accuracy of the summarization.  
- To address this, the team worked on reviewing the database relationships and integration points to ensure the tender matching and company profile data were properly connected.  

### Reflections on Teamwork and Leadership  
- This week highlighted the importance of clear communication and coordination when handling feature refinements.  
- As a team, we learned that close collaboration and regular check-ins are key to quickly identifying and resolving integration issues. The leadership encouraged open discussion and collective problem-solving, which helped the team stay focused and productive.

## Final Week Team Lead Report

**Lead:** Kelebogile Dlamini

---

## Responsibilities / Decisions Made

As we reached the final phase of the Tender Insight Hub project, our primary focus was on system integration, testing, and documentation. This stage involved connecting all previously developed modules and ensuring that the system functioned smoothly as a complete SaaS solution.

Key tasks and decisions included:

- Finalized the Company Profile Management feature and fully integrated it with the Match Tender functionality.
- Conducted end-to-end testing for all core features — keyword search, filtering, AI summarization, readiness scoring, and workspace tracking.
- Implemented final bug fixes and optimized database queries for both PostgreSQL (SQL) and MongoDB (NoSQL) components.
- Reviewed and updated API documentation on Swagger to reflect the final endpoints and usage examples.
- Ensured feature access restrictions based on SaaS tiers (Free, Basic, and Pro) were functioning as intended.
- Compiled and formatted all project documentation, including design reports, system flow diagrams, and individual team lead reports for submission.

---

## Challenges Faced and How They Were Addressed

### Integration Conflicts
Merging different components (especially the AI summarization with readiness scoring) caused minor data inconsistencies. These were resolved through joint debugging sessions and improved communication during version control operations.

### Performance Issues
During testing, we noticed delays in summarization for large tender documents. The issue was mitigated by caching summarized results in MongoDB to avoid repeated processing.

### Final Deployment Testing
The team encountered issues when deploying to the testing environment. After identifying missing dependencies in the FastAPI setup, we reconfigured the environment and confirmed successful deployment.

---

## Reflections on Teamwork and Leadership

This phase required strong coordination, as multiple features needed to work together seamlessly. As team lead, I emphasized consistent communication through daily updates and GitHub progress tracking.

Every team member demonstrated commitment and technical growth throughout the semester, contributing unique strengths to ensure the project’s success.

Leading the final week taught me the importance of attention to detail, collaborative debugging, and thorough testing before delivery.

I am proud of how far we have come — from setting up our FastAPI environment to delivering a fully functional AI-assisted tender management platform.

---

## Final Reflections on the Project

The Tender Insight Hub project has been an enriching learning experience. We successfully implemented a real-world solution that leverages AI integration, multi-database management, and modern web technologies to address challenges faced by SMEs in public procurement.

This project not only strengthened our technical skills in API development, data management, and AI integration but also enhanced our teamwork, leadership, and project management abilities. We are confident that the knowledge gained from this project will serve as a strong foundation for our future careers in ICT and software development.




