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

## Week 3 Team Lead Report
**Lead:** Kelebogile Dlamini

### Responsibilities / Decisions Made
This week, our focus was on the **Company Profile Management** feature.

- Worked on the Company Profile schema and discussed its required fields
- Decided that each team member should attempt to work on the Company Profile individually and present their solution during the next meeting to move forward.  
- Completed the AI summarization feature

### Key Decision Made
- Adopted a collaborative approach to Company Profile development by having all team members contribute individually.

### Challenges Faced and Solutions
- The Company Profile feature is still incomplete, which slowed progress. To solve this, everyone will work on their own version and merge ideas next week.  

### Reflections on Teamwork and Leadership
- Having all members contribute to the Company Profile feature encourages creativity and will help us find the best approach.

### Week 4 Team Lead Report  

**Lead:** Ayanda Girly Khalo  

---

### Key Decisions Made During Leadership  
- During this week’s team meetup, we received valuable insights from our supervisor regarding the AI summarization feature. Based on this feedback, we led the decision to integrate the summarization function with the search button. This allows the system to summarize all PDFs associated with a search query, ensuring that the summarization tool is practical and directly connected to user actions.  

### Challenges Faced and How They Were Addressed  
- One of the major challenges we encountered was retrieving documents from the API and correctly matching them with the relevant tender. This issue initially slowed down our progress, as it was critical to ensure that the summarization applied to the correct documents.  
- To address this, the team collaborated to refine our API calls and implement checks that improved document retrieval accuracy. Through iterative testing and adjustments, we managed to align the retrieved documents with the intended tenders.  

### Reflections on Teamwork and Leadership  
- This week’s experience reinforced the importance of teamwork and adaptability. As a team, we were open to guidance from our supervisor and used it constructively to refine our approach.  
- We learned that effective leadership is not only about making decisions but also about ensuring that the team stays focused on solving challenges collectively. Guiding the team through the API retrieval challenge also highlighted the importance of patience, communication, and encouraging problem-solving collaboration.  







