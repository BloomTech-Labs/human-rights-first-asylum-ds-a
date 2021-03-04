Known Defects:

1. Fields
    - All fields should be validated and fine-tuned for accuracy
        - more test data is necessary to do so
    - Field `get_applicant_determined_credibility` could be improved with fuzzy wuzzy,
    because the field's output is dependent on occurance of specific tokens in the document
    - Field `get_applicant_language` needs to be further refined to capture language names 
    that are both one- and two-words long
    - Field `get_applicant_indigenous_status` needs to be further refined to properly capture
    names of indigneous groups/nations that are longer and shorter than two words.
    - Field `get_applicant_determined_credibility` needs to have a wider search bredth, as to
    include the following search terms:
        a.    Consistent
        b.    Inconsistent/inconsistencies
        c.    Totality of the circumstances
        d.    Corroborating evidence
        e.    Documentary evidence
        f.    Burden
        g.    Testimony
        h.    Oral testimony
        i.    Explanation

2. API
    - Locally the API works but it takes about 20-45 seconds to run. This is a problem for Heroku. Heroku has a set max 30-second timeout limit and any request must be below this threshold. Currently, our TL, Robert Sharp, has been working on speeding it up. He may solve this problem before students run into it; however, future labs students may want to explore deploying to AWS. However, this is no easy task. A dependency named Poppler is required for the OCR and must be installed through Docker. Docker is hard to get deployed on AWS so finding a workaround with Robert may be a better approach. One way to get around the 30-second timeout is through background processes, but this will require more resources on Heroku.
3. Scraper Class
    - The scraper class works however is not completely optimized for efficiency and not always accurate. I would encourage future labs student to throw as many pdfs of case files through the scraper API locally and see if they can find and fix problems within the scraper class. As of right now, we have the scraper working as a proof of concept, but not as a viable and completely accurate product.

Please contact me Noah Nisbet on slack if you have any questions about the API since I wrote most of the code, but Robert Sharp is also very familiar with the code if you want to reach out to him too. I'm available for any clarifications if need be. Good luck guys!