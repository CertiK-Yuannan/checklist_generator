# """
# Checklist Generator module.
# Generates checklists by processing findings and existing templates using ChatGPT.
# """

# import logging
# import pandas as pd
# import json
# import os
# from pathlib import Path
# from typing import Dict, List, Any, Optional
# import openai

# logger = logging.getLogger(__name__)

# class ChecklistGenerator:
#     """Component to generate checklists from findings using ChatGPT."""
    
#     def __init__(self, category: str, api_key: str):
#         """
#         Initialize the checklist generator.
        
#         Args:
#             category: Category of findings being processed
#             api_key: OpenAI API key for ChatGPT
#         """
#         self.category = category
#         openai.api_key = api_key
#         self.checklist_dir = Path(__file__).parent.parent / "checklist"
        
#     def load_existing_checklist(self) -> Dict[str, Any]:
#         """
#         Load and parse existing checklist from markdown file.
        
#         Returns:
#             Dictionary containing parsed checklist data
#         """
#         checklist_path = self.checklist_dir / self.category / "preset_checklist.md"
#         intro_path = self.checklist_dir / self.category / "introduction.md"
        
#         try:
#             # Load introduction
#             if intro_path.exists():
#                 logger.info(f"Loading introduction from {intro_path}")
#                 with open(intro_path, 'r') as f:
#                     introduction = f.read().strip()
#             else:
#                 logger.warning(f"No introduction file found at {intro_path}")
#                 introduction = ""
            
#             # Load and parse checklist
#             if checklist_path.exists():
#                 logger.info(f"Loading checklist from {checklist_path}")
#                 with open(checklist_path, 'r') as f:
#                     markdown_content = f.read()
                
#                 # Parse markdown into JSON structure
#                 checklist_data = self._parse_markdown_to_json(markdown_content)
#             else:
#                 logger.warning(f"No checklist template found at {checklist_path}")
#                 checklist_data = []
#             return {
#                 "introduction": introduction,
#                 "checklist": checklist_data
#             }
                
#         except Exception as e:
#             logger.error(f"Error loading existing checklist: {e}")
#             raise
    
#     def _parse_markdown_to_json(self, markdown_content: str) -> List[Dict[str, Any]]:
#         """
#         Parse markdown checklist into JSON structure.
        
#         Args:
#             markdown_content: Raw markdown content
            
#         Returns:
#             List of checklist items with their structure
#         """
#         lines = markdown_content.split('\n')
#         checklist = []
#         current_item = None
#         current_sublist = None
        
#         for line in lines:
#             if not line.strip():
#                 continue
                
#             # Count leading spaces to determine level
#             leading_spaces = len(line) - len(line.lstrip())
#             level = leading_spaces // 2
#             content = line.strip()
            
#             # Handle different levels
#             if level == 0 and content.startswith('# '):
#                 # Main section
#                 if current_item:
#                     checklist.append(current_item)
#                 current_item = {
#                     "title": content[2:].strip(),
#                     "items": []
#                 }
#             elif level == 1 and content.startswith('- '):
#                 # Checklist item
#                 if current_item:
#                     item = {
#                         "text": content[2:].strip(),
#                         "subitems": []
#                     }
#                     current_item["items"].append(item)
#                     current_sublist = item["subitems"]
#             elif level == 2 and content.startswith('- '):
#                 # Sub-item
#                 if current_sublist is not None:
#                     current_sublist.append(content[2:].strip())
        
#         # Add the last item
#         if current_item:
#             checklist.append(current_item)
            
#         return checklist
    
#     def process_findings(self) -> Dict[str, Any]:
#         """
#         Process findings from CSV and generate updated checklist.
        
#         Returns:
#             Updated checklist data
#         """
#         # Load existing checklist
#         existing_data = self.load_existing_checklist()
        
#         # Load findings
#         findings_path = self.base_path / "findings" / f"solodit_findings_{self.category}.csv"
#         if not findings_path.exists():
#             logger.error(f"Findings file not found at {findings_path}")
#             raise FileNotFoundError(f"Findings file not found at {findings_path}")
        
#         logger.info(f"Loading findings from {findings_path}")
#         findings_df = pd.read_csv(findings_path)
        
#         # Process each finding with ChatGPT
#         updated_checklist = self._process_with_chatgpt(
#             existing_data,
#             findings_df
#         )
        
#         return updated_checklist
    
#     def _process_with_chatgpt(self, existing_data: Dict[str, Any], 
#                              findings_df: pd.DataFrame) -> Dict[str, Any]:
#         """
#         Process findings using ChatGPT to update the checklist.
        
#         Args:
#             existing_data: Existing checklist data
#             findings_df: DataFrame containing findings
            
#         Returns:
#             Updated checklist data
#         """
#         try:
#             # Prepare the context for ChatGPT
#             context = {
#                 "category": self.category,
#                 "existing_checklist": existing_data["checklist"],
#                 "introduction": existing_data["introduction"],
#                 "findings": findings_df.to_dict(orient='records')
#             }
            
#             # Format the prompt
#             prompt = self._create_prompt(context)
            
#             # Call ChatGPT API
#             logger.info("Calling ChatGPT API to process findings")
#             response = openai.ChatCompletion.create(
#                 model="gpt-4",
#                 messages=[
#                     {"role": "system", "content": "You are a security expert helping to generate and update security checklists based on findings."},
#                     {"role": "user", "content": prompt}
#                 ],
#                 temperature=0.7,
#                 max_tokens=2000
#             )
            
#             # Parse and validate the response
#             updated_data = self._parse_chatgpt_response(response.choices[0].message.content)
            
#             logger.info("Successfully processed findings with ChatGPT")
#             return updated_data
            
#         except Exception as e:
#             logger.error(f"Error processing with ChatGPT: {e}")
#             raise
    
#     def _create_prompt(self, context: Dict[str, Any]) -> str:
#         """
#         Create the prompt for ChatGPT.
        
#         Args:
#             context: Context information for the prompt
            
#         Returns:
#             Formatted prompt string
#         """
#         prompt = f"""
# Please analyze the following security findings related to {context['category']} and help update the security checklist.

# EXISTING INTRODUCTION:
# {context['introduction']}

# EXISTING CHECKLIST:
# {json.dumps(context['existing_checklist'], indent=2)}

# NEW FINDINGS:
# {json.dumps(context['findings'], indent=2)}

# Please:
# 1. Review the existing checklist and introduction
# 2. Analyze the new findings
# 3. Update or add checklist items based on the findings
# 4. Return the updated checklist in the same JSON format

# The response should be valid JSON with the following structure:
# {{
#     "introduction": "updated introduction text",
#     "checklist": [
#         {{
#             "title": "section title",
#             "items": [
#                 {{
#                     "text": "checklist item",
#                     "subitems": ["subitem 1", "subitem 2"]
#                 }}
#             ]
#         }}
#     ]
# }}
# """
#         return prompt
    
#     def _parse_chatgpt_response(self, response_text: str) -> Dict[str, Any]:
#         """
#         Parse and validate ChatGPT's response.
        
#         Args:
#             response_text: Raw response from ChatGPT
            
#         Returns:
#             Parsed and validated checklist data
#         """
#         try:
#             # Extract JSON from response (in case there's additional text)
#             start_idx = response_text.find('{')
#             end_idx = response_text.rindex('}') + 1
#             json_str = response_text[start_idx:end_idx]
            
#             # Parse JSON
#             updated_data = json.loads(json_str)
            
#             # Validate structure
#             if not isinstance(updated_data, dict):
#                 raise ValueError("Response is not a dictionary")
#             if "introduction" not in updated_data:
#                 raise ValueError("Response missing 'introduction' field")
#             if "checklist" not in updated_data:
#                 raise ValueError("Response missing 'checklist' field")
                
#             return updated_data
            
#         except Exception as e:
#             logger.error(f"Error parsing ChatGPT response: {e}")
#             logger.debug(f"Raw response: {response_text}")
#             raise
    
#     def save_checklist(self, checklist_data: Dict[str, Any]) -> None:
#         """
#         Save the updated checklist back to files.
        
#         Args:
#             checklist_data: Updated checklist data to save
#         """
#         try:
#             output_dir = self.base_path / "output"
#             os.makedirs(output_dir, exist_ok=True)
            
#             # Save introduction
#             intro_path = output_dir / f"{self.category}_intro_updated.md"
#             with open(intro_path, 'w') as f:
#                 f.write(checklist_data["introduction"])
            
#             # Save checklist
#             checklist_path = output_dir / f"{self.category}_checklist_updated.md"
#             with open(checklist_path, 'w') as f:
#                 f.write(self._convert_to_markdown(checklist_data["checklist"]))
                
#             logger.info(f"Updated checklist saved to {checklist_path}")
#             logger.info(f"Updated introduction saved to {intro_path}")
            
#         except Exception as e:
#             logger.error(f"Error saving updated checklist: {e}")
#             raise
    
#     def _convert_to_markdown(self, checklist: List[Dict[str, Any]]) -> str:
#         """
#         Convert checklist data back to markdown format.
        
#         Args:
#             checklist: Checklist data in JSON format
            
#         Returns:
#             Formatted markdown string
#         """
#         markdown_lines = []
        
#         for section in checklist:
#             # Add section title
#             markdown_lines.append(f"# {section['title']}\n")
            
#             # Add items
#             for item in section['items']:
#                 markdown_lines.append(f"- {item['text']}")
#                 # Add subitems
#                 for subitem in item['subitems']:
#                     markdown_lines.append(f"  - {subitem}")
#                 markdown_lines.append("")  # Empty line between items
                
#             markdown_lines.append("")  # Empty line between sections
            
#         return "\n".join(markdown_lines)