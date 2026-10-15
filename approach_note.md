# Approach Note

###### Extraction Approach



* *The system uses a multimodal LLM (LLaMA via Groq API) to extract structured academic data from marksheets provided as images or PDFs. PDFs are first converted into images using Poppler to ensure uniform processing. Each page is processed independently to avoid information loss in multi-page documents.*



**The prompt enforces:**



* *Strict JSON output*



* *Fixed field schema*



* *No hallucinated or inferred values*



* *Explicit nulls where data is not present*



* *Bounding boxes are derived from the model’s spatial understanding of the document and mapped back to extracted fields.*



##### Confidence Logic



* *Confidence scores are calculated using a hybrid approach:*



* *Model self-confidence (log-probability / certainty signal from the LLM)*



* *Text clarity (OCR confidence and visual sharpness)*



* *Cross-field validation (e.g., totals matching subject sums, consistent roll numbers)*



* *Final confidence is normalized between 0 and 1 for each field.*
* 
*This ensures confidence is interpretable and meaningful, not arbitrary.*



##### **Design Choices**



* *FastAPI for async concurrency and high throughput*



* *Stateless API for easy horizontal scaling*



* *Batch endpoint to reduce overhead and improve performance*



* *Strict schema enforcement to improve extraction reliability*



* *Frontend demo to validate real-world usability*



###### **API Authentication**



*Authentication is handled via API keys passed in request headers.*

*All secrets are stored in environment variables and never committed to the repository*.



###### **Extra Considerations**



* *Supports multiple concurrent requests*



* *Handles large files and invalid formats gracefully*



* *Works for both images and PDFs*



* *Easily extensible to other document types*
