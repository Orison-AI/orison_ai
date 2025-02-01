#! /usr/bin/env python3.11

# ==========================================================================
#  Copyright (c) Orison AI, 2024.
#
#  All rights reserved. All hardware and software names used are registered
#  trade names and/or registered trademarks of the respective manufacturers.
#
#  The user of this computer program acknowledges that the above copyright
#  notice, which constitutes the Universal Copyright Convention, will be
#  attached at the position in the function of the computer program which the
#  author has deemed to sufficiently express the reservation of copyright.
#  It is prohibited for customers, users and/or third parties to remove,
#  modify or move this copyright notice.
# ==========================================================================

# External

import asyncio
from typing import List, Dict
from langgraph.graph import Graph, StateGraph

# Internal

from or_store.firebase import OrisonSecrets
from or_store.db_interfaces import GoogleScholarClient, ScreeningClient, EvidenceClient
from or_store.models import EvidenceBuilder
from or_llm.orison_messenger import OrisonMessenger


class CoverLetterGenerator:
    def __init__(self, secrets):
        self.llm = OrisonMessenger(secrets=secrets)._system_chain

    async def fetch_scholar_info(self, attorney_id: str, applicant_id: str) -> Dict:
        scholar_client = GoogleScholarClient()
        scholar_info, _ = await scholar_client.find_top(attorney_id, applicant_id)
        return scholar_info.to_json()

    async def fetch_screening_info(self, attorney_id: str, applicant_id: str) -> List:
        screening_client = ScreeningClient()
        screening_info, _ = await screening_client.find_top(attorney_id, applicant_id)
        return [qna.answer for qna in screening_info.summary]

    async def generate_section(self, criterion: str, details: Dict) -> str:
        prompt = (
            f'Write a detailed cover letter section explaining how the candidate meets the following criterion: "{criterion}". '
            f"Include the provided details: {details}. Use simple language understandable by a 6th grader."
        )
        # Ensure the response is a string
        response = await self.llm.ainvoke(prompt)
        return (
            response["text"]
            if isinstance(response, dict) and "text" in response
            else str(response)
        )

    async def process_evidence(self, criteria: List[str], details: Dict) -> List[str]:
        async def process_criterion(criterion):
            result = await self.generate_section(criterion, details)
            return result.strip()  # Ensure valid strings

        tasks = [process_criterion(criterion) for criterion in criteria]
        return await asyncio.gather(*tasks)

    async def generate_letter(self, attorney_id: str, applicant_id: str) -> str:
        evidence_criteria = [
            "Evidence of receipt of lesser nationally or internationally recognized prizes or awards for excellence",
            "Evidence of your membership in associations in the field which demand outstanding achievement of their members",
            "Evidence of published material about you in professional or major trade publications or other major media",
            "Evidence that you have been asked to judge the work of others, either individually or on a panel",
            "Evidence of your original scientific, scholarly, artistic, athletic, or business-related contributions of major significance to the field",
            "Evidence of your authorship of scholarly articles in professional or major trade publications or other major media",
            "Evidence that your work has been displayed at artistic exhibitions or showcases",
            "Evidence of your performance of a leading or critical role in distinguished organizations",
            "Evidence that you command a high salary or other significantly high remuneration in relation to others in the field",
            "Evidence of your commercial successes in the performing arts",
            "Evidence of receipt of major prizes or awards for outstanding achievement",
            "Evidence of membership in associations that require their members to demonstrate outstanding achievement",
            "Evidence of published material in professional publications written by others about the noncitizen's work in the academic field",
            "Evidence of participation, either on a panel or individually, as a judge of the work of others in the same or allied academic field",
            "Evidence of original scientific or scholarly research contributions in the field",
            "Evidence of authorship of scholarly books or articles (in scholarly journals with international circulation) in the field",
        ]

        scholar_info = await self.fetch_scholar_info(attorney_id, applicant_id)
        screening_info = await self.fetch_screening_info(attorney_id, applicant_id)
        details = {"scholar_info": scholar_info, "screening_info": screening_info}

        # Process evidence criteria in parallel
        results = await self.process_evidence(evidence_criteria, details)
        valid_sections = [result for result in results if result]

        # Build the letter using a predefined template
        template = (
            "The achievement-based immigrant visa category is reserved for persons of extraordinary ability in the sciences, arts, education, "
            "business, or athletics. To qualify for the category, the candidate must demonstrate extraordinary ability through sustained national or "
            "international acclaim and the candidate's achievements must be recognized in the candidate's field through extensive documentation. \n\n"
            "Thus, as an AI assistant, I present the evidence supporting {candidate_name}'s application.\n\n"
            "{evidence_sections}\n\n"
            "Thank you for considering this detailed application for {candidate_name}."
        )

        full_cover_letter = template.format(
            candidate_name="the candidate",
            evidence_sections="\n\n".join(valid_sections),
        )

        # Save to the database
        evidence_client = EvidenceClient()
        evidence_letter = EvidenceBuilder(summary=full_cover_letter)
        await evidence_client.insert(
            attorney_id=attorney_id,
            applicant_id=applicant_id,
            doc=evidence_letter,
        )

        return full_cover_letter


if __name__ == "__main__":

    async def main():
        attorney_id = "xlMsyQpatdNCTvgRfW4TcysSDgX2"
        applicant_id = "tYdtBdc7lJHyVCxquubj"
        secrets = OrisonSecrets.from_attorney_applicant(attorney_id, applicant_id)
        generator = CoverLetterGenerator(secrets=secrets)
        letter = await generator.generate_letter(attorney_id, applicant_id)
        print(letter)

    asyncio.run(main())
