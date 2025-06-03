# # import os
# # from app.log import logger
# # from openai import OpenAI


# # # Ensure this path is correct relative to where you run setup_assistant.py
# # try:
# #     from app.config import Config
# # except ImportError:
# #     print("Error: Could not import app.config. Make sure you are running this script from the project root or the app directory.")
# #     print("Also ensure app/config.py exists and python-dotenv is installed.")
# #     exit(1)

# # # Configure logger

# # # Load env variables FIRST
# # try:
# #     Config.load_env()
# #     logger.info("Environment variables loaded successfully.")
# # except Exception as e:
# #     logger.error(f"Failed to load environment variables: {e}")
# #     exit(1)

# # # Get existing assistant ID from config if it exists
# # ASSISTANT_ID = Config.OPENAI_ASSISTANT_ID

# # client = OpenAI(api_key=Config.OPENAI_API_KEY)

# # # --- Define the tool function descriptions ---
# # # These tell the OpenAI model WHEN and HOW to call your functions.
# # # The actual function execution happens in your application code.

# # tool_definitions = [
# #     {
# #         "type": "function",
# #         "function": {
# #             "name": "collect_scheduling_info",
# #             "description": "Collects necessary information (name, email, phone number, desired date/time) from the user for scheduling a meeting. Call this when the user expresses interest in scheduling a meeting and you have gathered some or all of these details. You should extract the details from the user's messages.",
# #             "parameters": {
# #                 "type": "object",
# #                 "properties": {
# #                     "name": {
# #                         "type": "string",
# #                         "description": "The full name of the user."
# #                     },
# #                     "email": {
# #                         "type": "string",
# #                         "description": "The email address of the user."
# #                     },
# #                     "phone": {
# #                         "type": "string",
# #                         "description": "The phone number of the user."
# #                     },
# #                     "datetime": {
# #                          "type": "string",
# #                          "description": "The requested date and time for the meeting (e.g., 'tomorrow at 2pm', 'June 1st 2024 10:30 AM'). Extract the most specific information provided."
# #                     }
# #                 },
# #                 # Indicate which parameters are absolutely required for the Assistant to call THIS function.
# #                 # Even if not all are required *to call* the function, the Assistant should know it needs
# #                 # to ideally get all of them before scheduling.
# #                 # Let's say the Assistant should try to call this once it has name AND at least one contact method OR datetime.
# #                 # Or, simpler, call it when it feels it has gathered some info for scheduling.
# #                 "required": ["name", "datetime"] # Example: Require name and date/time to trigger this
# #                 # Adjust required based on when you want the Assistant to signal it has info.
# #                 # If you want it to signal as soon as it gets *any* info, make none required.
# #                 # If you want it to signal when it thinks it has *all* key info, make them all required.
# #                 # Let's make none strictly required for the *call* itself, but the description guides the AI.
# #                 # The AI should still aim to get all info before the *scheduling* step.
# #                 # "required": [] # None required just to trigger info collection acknowledgement
# #             }
# #         }
# #     },
# #     {
# #         "type": "function",
# #         "function": {
# #             "name": "schedule_meeting_with_dr_inae",
# #             "description": "Schedules a meeting specifically with Dr. Inae using the user's collected information. Call this ONLY when the user explicitly confirms they want to schedule a meeting with Dr. Inae AND you have confirmed you have their full name, email, phone number, and the specific date/time for the meeting.",
# #             "parameters": {
# #                 "type": "object",
# #                 "properties": {
# #                     "name": {
# #                         "type": "string",
# #                         "description": "The full name of the user.",
# #                          # These are required for the *scheduling* action
# #                     },
# #                     "email": {
# #                         "type": "string",
# #                         "description": "The email address of the user.",
                        
# #                     },
# #                     "phone": {
# #                         "type": "string",
# #                         "description": "The phone number of the user.",
# #                     },
# #                     "datetime": {
# #                          "type": "string",
# #                          "description": "The confirmed date and time for the meeting (e.g., '2024-06-01T10:30:00'). Ensure this is a specific date and time.",
                         
# #                     }
# #                 },
# #                 "required": ["name", "email", "phone", "datetime"] # ALL required to schedule
# #             }
# #         }
# #     },
# #     {
# #         "type": "function",
# #         "function": {
# #             "name": "transfer_chat_to_whatsapp",
# #             "description": "Transfers the chat to a human agent. Call this when the user explicitly asks to speak to a human, transfer the chat, or indicates the HR bot cannot resolve their issue. The bot will provide a message to the user indicating how to contact the human.",
# #             "parameters": {
# #                  "type": "object",
# #                  "properties": {
# #                       "message_to_user": {
# #                            "type": "string",
# #                            "description": "(Optional) A brief message the assistant wants to include when initiating the transfer notification to the user, e.g., summarizing the issue."
# #                       }
# #                  },
# #                  "required": [] # No arguments strictly required to trigger a transfer
# #             }
# #         }
# #     }
# #     # Add the file_search tool if you still need it
# #     #{"type": "file_search"}
# # ]


# # def create_or_update_assistant():
# #     global ASSISTANT_ID

# #     # Update instructions to reflect new capabilities
# #     instructions = """
# # ## Identity
# # Você é Ana, recepcionista da clínica da Dra. Inaê Almeida em Jundiaí, São Paulo. Você é uma recepcionista simpática e atenciosa, que se preocupa profundamente com os pacientes. Você não fornece aconselhamento médico, mas usa seu conhecimento médico para entender as respostas dos pacientes.


# # ##Note
# # Today's date is : 12/04/2025

# # ## Style Guidelines
# # Be Concise: Respond succinctly, addressing one topic at a time.
# # You chat in Portuguese only.
# # Adopt Variety: Use diverse language and rephrasing to improve clarity without repeating content.
# # Be Conversational: Use everyday language, making the conversation sound like a conversation with a friend.
# # Be Proactive: Lead the conversation, often concluding with a question or suggestion for a next step.
# # Avoid Multiple Questions: Ask only one question at a time.
# # Aim for Clarity: If the patient provides a partial or unclear answer, ask follow-up questions to ensure understanding.
# # Use Colloquial Dates: Refer to dates in a conversational manner, such as “Friday, January 14” or “Tuesday, January 12, 2024, at 8:00 AM.”
# # ## Response Guidelines
# # Adapt and Guess: Try to understand responses that may contain errors. Avoid mentioning “transcription error” in your responses.
# # Stay in Character: Keep conversations within the scope of your role by directing them back to you in creative ways without repeating yourself.
# # Ensure Fluent Dialogue: Respond in a role-appropriate and direct manner to maintain a smooth conversational flow.



# # ## Background
# # 1. Pricing
# # a. Consulta Integral  R$ 710,00
# # b. Consulta simples/acompanhamento R$ 470,00
# # c.  Acupuntura: R$ 130,00
 
# # 2. ⁠timings
# # a. Consultas: Segunda a Quinta Feira: 07:30 as 12:00
# # b. Acupuntura: Quinta-feira das 7:30 as 11:00


# # 3. ⁠doctor information
# # a. Por que escolher a Dra. Inaê Almeida?
# #                                             i. Pioneira em Saúde da Mulher Liderando os cuidados de saúde da mulher em Jundiaí.
# #                                           ii. Integrativa e Preventiva Especialista em bem-estar abrangente.
# #                                           iii. Especialista Certificada Medicina Interna, Acupuntura e Medicina Ortomolecular.
# #                                           iv. Atendimento Centrado no Paciente Tratamentos embasados na ciência, personalizados
# # b. Formação Acadêmica:
# #                                             i. Formação Faculdade de Medicina de Jundiai
# #                                           ii. Residência de Clinica medica e título de especialista pela Sociedade Brasileira de clínica Médica
# #                                           iii. Residência em Medicina Interna no Hospital Ipiranga
# #                                           iv. Pós Graduação em medicina chinesa e Acupuntura pela universidade federal de São Paulo
# #                                           v. Pós Graduação em Medicina Funcional e ortomolecular pela Fapes
# #                                           vi. Tratamento integrativo da saúde feminina.
# # 4. ⁠treatment on offer
# # a. Áreas de Especialidade
# # b. Medicina Interna Diagnóstico e tratamento de pacientes adultos. Ampla gama de condições não cirúrgicas.
# # c.  Acupuntura Terapia chinesa antiga. Fortalecimento do sistema imunológico e tratamento de problemas emocionais e físicos.
# # d. Medicina do Estilo de Vida Abordagens baseadas em evidências. Nutrição, atividade, sono, gerenciamento do estresse para o bem-estar
 
# # 5. ⁠location :
# # a. Rua Adhemar Pereira de Barros, 21 consultório 62, Vila Boaventura
 
# # b. Jundiaí/SPTelefone:
# #                                             i. (11) 4521-2542
# #                                           ii. (11) 97606-1625
 
# # 6. ⁠how treatment works
# # a. Cuidados Abrangentes Cuidados especializados em todas as fases da vida.
# # b. Focado em prevenção, diagnóstico precoce e tratamento.
 

# # 7. Payment plan
# # a. Dinheiro
# # b. PIX
# # c.  Transferência bancaria
# # d. Cheque


# # ## Tarefa
# # 1. Verifique se este é o primeiro contato do usuário com a clínica ou se ele já entrou em contato antes.
# # 2. Pergunte ao usuário o que o tem incomodado e qual serviço ele procura, se houver algum específico.
# # 3. Determine o nível de urgência da consulta do usuário — se ele deseja agendá-la agora ou mais tarde.
# # 4. Explique brevemente que a Dra. Inae oferece consultas em Clínica Geral, Acupuntura e Medicina do Estilo de Vida.
# # 5. Pergunte se ele deseja que você destaque as características únicas ou se tem alguma dúvida que terá prazer em esclarecer.
# # - Se destacar a singularidade da clínica, informe sobre o foco em saúde equilibrada e sustentável e a dedicação da Dra. Inae ao cuidado integral.
# # - Se houver alguma dúvida, esclareça-a com base em #backgrounf ou na base de conhecimento.
# # 6. Reconheça as preocupações do usuário sobre o custo e enfatize os benefícios a longo prazo da consulta. Mencione que opções de pagamento flexíveis estão disponíveis.
# # #Regra
# # Transição para o nó Agendar Compromisso se o usuário quiser agendar, mas não mencionar isso no chat"""
# #     name = "Dra. Inaê Almeida - Assistente Virtual"
# #     model = "gpt-4o-mini" # Or another suitable model like gpt-3.5-turbo if preferred for cost/speed

# #     # Combine function tools and file search tool
# #     tools_list = tool_definitions
# #     # if you need file search, uncomment below and ensure vector_store_ids are handled
# #     # tools_list.append({"type": "file_search"})


# #     # IMPORTANT: If using file_search, you need to manage vector_store_ids.
# #     # You typically create a vector store first (client.beta.vector_stores.create),
# #     # upload files to it (client.beta.vector_stores.files.upload), and then
# #     # associate the vector store ID with the assistant.
# #     # If you are just adding function calling for now and not using file search yet:
# #     tool_resources_config = {} # No tool resources needed if only using function calling

# #     # If you ARE using file search with a specific vector store:
# #     # Replace 'vs_YOUR_VECTOR_STORE_ID' with your actual Vector Store ID
# #     # tool_resources_config = {"file_search": {"vector_store_ids": ["vs_YOUR_VECTOR_STORE_ID"]}}
# #     # Ensure the file_search tool is also in the tools_list above


# #     if ASSISTANT_ID:
# #         try:
# #             logger.info(f"Attempting to retrieve existing assistant: {ASSISTANT_ID}")
# #             assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
# #             logger.info("Assistant found. Updating configuration...")
# #             # Note: Updating tool_resources is tricky. If changing file_search, you
# #             # need to specify the *new* vector_store_ids array.
# #             assistant = client.beta.assistants.update(
# #                 assistant.id,
# #                 instructions=instructions,
# #                 name=name,
# #                 model=model,
# #                 tools=tools_list, # Update with the new tools list
# #                 # tool_resources=tool_resources_config # Uncomment if updating file search resources
# #             )
# #             logger.info("Assistant updated successfully!")
# #         except Exception as e:
# #             logger.error(f"Error retrieving or updating assistant {ASSISTANT_ID}: {e}")
# #             logger.info("Creating a new assistant instead.")
# #             ASSISTANT_ID = None # Force creation

# #     if not ASSISTANT_ID:
# #         logger.info("Creating a new assistant...")
# #         try:
# #             assistant = client.beta.assistants.create(
# #                 instructions=instructions,
# #                 name=name,
# #                 tools=tools_list, # Use the defined tools list
# #                 model=model,
# #                 tool_resources=tool_resources_config # Add tool resources if needed (e.g., file search)
# #             )
# #             logger.info("New assistant created successfully!")
# #             ASSISTANT_ID = assistant.id
# #         except Exception as e:
# #              logger.error(f"Error creating assistant: {e}")
# #              return # Exit function if creation fails


# #     logger.info(f"Assistant ID: {ASSISTANT_ID}")
# #     logger.info("Please add or update OPENAI_ASSISTANT_ID in your .env file with this ID.")
# #     # Simple way to try and write to .env - use with caution!
# #     env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
# #     try:
# #         with open(env_path, 'r') as f:
# #             lines = f.readlines()
# #         with open(env_path, 'w') as f:
# #             updated = False
# #             for line in lines:
# #                 if line.strip().startswith('OPENAI_ASSISTANT_ID='):
# #                     f.write(f'OPENAI_ASSISTANT_ID={ASSISTANT_ID}\n')
# #                     updated = True
# #                 else:
# #                     f.write(line)
# #             if not updated:
# #                 f.write(f'\nOPENAI_ASSISTANT_ID={ASSISTANT_ID}\n')
# #         logger.info(".env file updated successfully.")
# #     except Exception as e:
# #         logger.warning(f"Could not automatically write to {env_path}. Please update it manually.")
# #         logger.info(f"Manual update needed: OPENAI_ASSISTANT_ID={ASSISTANT_ID}")


# #     logger.info("Assistant setup completed successfully.")
# #     print("\nAssistant Details:")
# #     print(assistant)


# # if __name__ == "__main__":
# #     try:
# #         create_or_update_assistant()
# #     except Exception as e:
# #         logger.critical(f"Unhandled exception in setup_assistant: {e}")












# import os
# from openai import OpenAI
# try:
#     from app.config import Config
# except ImportError:
#     print("Error: Could not import app.config. Make sure you are running this script from the project root or the app directory.")
#     print("Also ensure app/config.py exists and python-dotenv is installed.")
#     exit(1)

# #Config.load_env()

# ASSISTANT_ID = Config.OPENAI_ASSISTANT_ID

# client = OpenAI(api_key=Config.OPENAI_API_KEY)

# # --- Define the tool function descriptions ---

# tool_definitions = [
#     {
#         "type": "function",
#         "function": {
#             "name": "collect_scheduling_info",
#             "description": "Extracts and acknowledges key details (name, email, phone number, desired date/time) from the user's message for scheduling a meeting. Call this when the user mentions scheduling or provides relevant contact/time information.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "name": {"type": "string", "description": "The full name of the user."},
#                     "email": {"type": "string", "description": "The email address of the user."},
#                     "phone": {"type": "string", "description": "The phone number of the user."},
#                     "datetime": {"type": "string", "description": "The requested date and time for the meeting (e.g., 'tomorrow at 2pm', 'June 1st 2024 10:30 AM'). Extract the most specific information provided."}
#                 },
#                 "required": []
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "schedule_meeting_with_dr_inae",
#             "description": "Schedules a meeting specifically with Dr. Inae using the user's confirmed information. Call this ONLY after the user explicitly confirms they want to book the meeting AND you have successfully gathered their full name, email, phone number, AND a specific date and time. Provide these four pieces of information as parameters.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "name": {"type": "string", "description": "The full name of the user."},
#                     "email": {"type": "string", "description": "The email address of the user."},
#                     "phone": {"type": "string", "description": "The phone number of the user."},
#                     "datetime": {"type": "string", "description": "The FINAL, confirmed, specific date and time for the meeting (e.g., '2024-06-01 10:30 AM')."}
#                 },
#                 "required": ["name", "email", "phone", "datetime"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "transfer_chat_to_whatsapp",
#             "description": "Transfers the chat to a human agent. Call this when the user explicitly asks to speak to a human or indicates they need help beyond the bot's capabilities. When calling, include the user's name if known, and a summary of the conversation so far.",
#             "parameters": {
#                  "type": "object",
#                  "properties": {
#                       "user_name": { # New parameter for user's name
#                            "type": "string",
#                            "description": "The name of the user, if it was provided during the conversation."
#                       },
#                       "conversation_summary": { # New parameter for summary
#                            "type": "string",
#                            "description": "A brief summary of the conversation history and the user's reason for needing to transfer to a human."
#                       },
#                       "message_to_user": {
#                            "type": "string",
#                            "description": "(Optional) A brief message the assistant wants to include when initiating the transfer notification to the user, e.g., summarizing the issue."
#                       }
#                  },
#                  "required": ["conversation_summary"] # Require a summary for the transfer
#             }
#         }
#     }
#     # Add file_search if needed
#     # {"type": "file_search"}
# ]


# def create_or_update_assistant():
#     global ASSISTANT_ID

#     instructions = """
    
# # ## Identity
# # Você é Ana, recepcionista da clínica da Dra. Inaê Almeida em Jundiaí, São Paulo. Você é uma recepcionista simpática e atenciosa, que se preocupa profundamente com os pacientes. Você não fornece aconselhamento médico, mas usa seu conhecimento médico para entender as respostas dos pacientes.


# # ##Note
# # Today's date is : 12/04/2025

# # ## Style Guidelines
# # Be Concise: Respond succinctly, addressing one topic at a time.
# # You chat in Portuguese only.
# # Adopt Variety: Use diverse language and rephrasing to improve clarity without repeating content.
# # Be Conversational: Use everyday language, making the conversation sound like a conversation with a friend.
# # Be Proactive: Lead the conversation, often concluding with a question or suggestion for a next step.
# # Avoid Multiple Questions: Ask only one question at a time.
# # Aim for Clarity: If the patient provides a partial or unclear answer, ask follow-up questions to ensure understanding.
# # Use Colloquial Dates: Refer to dates in a conversational manner, such as “Friday, January 14” or “Tuesday, January 12, 2024, at 8:00 AM.”
# # ## Response Guidelines
# # Adapt and Guess: Try to understand responses that may contain errors. Avoid mentioning “transcription error” in your responses.
# # Stay in Character: Keep conversations within the scope of your role by directing them back to you in creative ways without repeating yourself.
# # Ensure Fluent Dialogue: Respond in a role-appropriate and direct manner to maintain a smooth conversational flow.



# # ## Background
# # 1. Pricing
# # a. Consulta Integral  R$ 710,00
# # b. Consulta simples/acompanhamento R$ 470,00
# # c.  Acupuntura: R$ 130,00
 
# # 2. ⁠timings
# # a. Consultas: Segunda a Quinta Feira: 07:30 as 12:00
# # b. Acupuntura: Quinta-feira das 7:30 as 11:00


# # 3. ⁠doctor information
# # a. Por que escolher a Dra. Inaê Almeida?
# #                                             i. Pioneira em Saúde da Mulher Liderando os cuidados de saúde da mulher em Jundiaí.
# #                                           ii. Integrativa e Preventiva Especialista em bem-estar abrangente.
# #                                           iii. Especialista Certificada Medicina Interna, Acupuntura e Medicina Ortomolecular.
# #                                           iv. Atendimento Centrado no Paciente Tratamentos embasados na ciência, personalizados
# # b. Formação Acadêmica:
# #                                             i. Formação Faculdade de Medicina de Jundiai
# #                                           ii. Residência de Clinica medica e título de especialista pela Sociedade Brasileira de clínica Médica
# #                                           iii. Residência em Medicina Interna no Hospital Ipiranga
# #                                           iv. Pós Graduação em medicina chinesa e Acupuntura pela universidade federal de São Paulo
# #                                           v. Pós Graduação em Medicina Funcional e ortomolecular pela Fapes
# #                                           vi. Tratamento integrativo da saúde feminina.
# # 4. ⁠treatment on offer
# # a. Áreas de Especialidade
# # b. Medicina Interna Diagnóstico e tratamento de pacientes adultos. Ampla gama de condições não cirúrgicas.
# # c.  Acupuntura Terapia chinesa antiga. Fortalecimento do sistema imunológico e tratamento de problemas emocionais e físicos.
# # d. Medicina do Estilo de Vida Abordagens baseadas em evidências. Nutrição, atividade, sono, gerenciamento do estresse para o bem-estar
 
# # 5. ⁠location :
# # a. Rua Adhemar Pereira de Barros, 21 consultório 62, Vila Boaventura
 
# # b. Jundiaí/SPTelefone:
# #                                             i. (11) 4521-2542
# #                                           ii. (11) 97606-1625
 
# # 6. ⁠how treatment works
# # a. Cuidados Abrangentes Cuidados especializados em todas as fases da vida.
# # b. Focado em prevenção, diagnóstico precoce e tratamento.
 

# # 7. Payment plan
# # a. Dinheiro
# # b. PIX
# # c.  Transferência bancaria
# # d. Cheque


# # ## Tarefa
# # 1. Verifique se este é o primeiro contato do usuário com a clínica ou se ele já entrou em contato antes.
# # 2. Pergunte ao usuário o que o tem incomodado e qual serviço ele procura, se houver algum específico.
# # 3. Determine o nível de urgência da consulta do usuário — se ele deseja agendá-la agora ou mais tarde.
# # 4. Explique brevemente que a Dra. Inae oferece consultas em Clínica Geral, Acupuntura e Medicina do Estilo de Vida.
# # 5. Pergunte se ele deseja que você destaque as características únicas ou se tem alguma dúvida que terá prazer em esclarecer.
# # - Se destacar a singularidade da clínica, informe sobre o foco em saúde equilibrada e sustentável e a dedicação da Dra. Inae ao cuidado integral.
# # - Se houver alguma dúvida, esclareça-a com base em #backgrounf ou na base de conhecimento.
# # 6. Reconheça as preocupações do usuário sobre o custo e enfatize os benefícios a longo prazo da consulta. Mencione que opções de pagamento flexíveis estão disponíveis.
# # #Regra
# # Transição para o nó Agendar Compromisso se o usuário quiser agendar, mas não mencionar isso no chat
    
    
# """

#     name = "HR Helper"
#     model = "gpt-4o" # Or another suitable model

#     tools_list = tool_definitions
#     # if you need file search, uncomment below and ensure vector_store_ids are handled
#     # tools_list.append({"type": "file_search"})

#     # tool_resources configuration for file_search if used
#     tool_resources_config = {}
#     # Example if using file search with a vector store:
#     # tool_resources_config = {"file_search": {"vector_store_ids": ["vs_YOUR_VECTOR_STORE_ID"]}}


#     if ASSISTANT_ID:
#         try:
#             print(f"Attempting to retrieve existing assistant: {ASSISTANT_ID}")
#             assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
#             print(f"Assistant found. Updating configuration...")
#             assistant = client.beta.assistants.update(
#                 assistant.id,
#                 instructions=instructions,
#                 name=name,
#                 model=model,
#                 tools=tools_list,
#                 # tool_resources=tool_resources_config
#             )
#             print("Assistant updated successfully!")
#         except Exception as e:
#             print(f"Error retrieving or updating assistant {ASSISTANT_ID}: {e}")
#             print("Creating a new assistant instead.")
#             ASSISTANT_ID = None

#     if not ASSISTANT_ID:
#         print("Creating a new assistant...")
#         try:
#             assistant = client.beta.assistants.create(
#                 instructions=instructions,
#                 name=name,
#                 tools=tools_list,
#                 model=model,
#                 tool_resources=tool_resources_config
#             )
#             print("New assistant created successfully!")
#             ASSISTANT_ID = assistant.id
#         except Exception as e:
#              print(f"Error creating assistant: {e}")
#              return


#     print(f"\nAssistant ID: {ASSISTANT_ID}")
#     print("Please add or update OPENAI_ASSISTANT_ID in your .env file with this ID.")
#     env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
#     try:
#         with open(env_path, 'r') as f:
#             lines = f.readlines()
#         with open(env_path, 'w') as f:
#             updated = False
#             for line in lines:
#                 if line.strip().startswith('OPENAI_ASSISTANT_ID='):
#                     f.write(f'OPENAI_ASSISTANT_ID={ASSISTANT_ID}\n')
#                     updated = True
#                 else:
#                     f.write(line)
#             if not updated:
#                 f.write(f'\nOPENAI_ASSISTANT_ID={ASSISTANT_ID}\n')
#         print(f".env file updated with OPENAI_ASSISTANT_ID={ASSISTANT_ID}")
#     except Exception as e:
#         print(f"Warning: Could not automatically write to {env_path}. Please update it manually.")
#         print(f"Manual update needed: OPENAI_ASSISTANT_ID={ASSISTANT_ID}")


#     print("\nAssistant Details:")
#     print(assistant)


# if __name__ == "__main__":
#     create_or_update_assistant()










# import os
# from openai import OpenAI
# try:
#     from app.config import Config
# except ImportError:
#     print("Error: Could not import app.config. Make sure you are running this script from the project root or the app directory.")
#     print("Also ensure app/config.py exists and python-dotenv is installed.")
#     exit(1)

# # Config.load_env() # Loading happens on import now

# ASSISTANT_ID = Config.OPENAI_ASSISTANT_ID

# client = OpenAI(api_key=Config.OPENAI_API_KEY)

# # --- Define the tool function descriptions (keep these as they were, but description refined) ---
# tool_definitions = [
#     {
#         "type": "function",
#         "function": {
#             "name": "collect_scheduling_info",
#             "description": "Extracts and acknowledges key details (name, email, phone number, desired date/time) from the user's message for scheduling a meeting. Call this when the user mentions scheduling or provides relevant contact/time information.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "name": {"type": "string", "description": "The full name of the user."},
#                     "email": {"type": "string", "description": "The email address of the user."},
#                     "phone": {"type": "string", "description": "The phone number of the user."},
#                     "datetime": {"type": "string", "description": "The requested date and time for the meeting (e.g., 'tomorrow at 2pm', 'June 1st 2025 11:00 AM'). Extract the most specific information provided."}
#                 },
#                 "required": []
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "schedule_meeting_with_dr_inae",
#             "description": "Attempts to schedule a meeting specifically with Dr. Inae using the user's confirmed information. Call this ONLY after the user explicitly confirms they want to book the meeting AND you have successfully gathered their full name, email, phone number, AND a specific date and time. Provide these four pieces of information as parameters. The tool will check for availability and finalize the booking.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "name": {"type": "string", "description": "The full name of the user."},
#                     "email": {"type": "string", "description": "The email address of the user."},
#                     "phone": {"type": "string", "description": "The phone number of the user."},
#                     "datetime": {"type": "string", "description": "The FINAL, confirmed, specific date and time requested by the user (e.g., '2025-06-01 10:30 AM')."}
#                 },
#                 "required": ["name", "email", "phone", "datetime"] # ALL required to attempt scheduling
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "transfer_chat_to_whatsapp",
#             "description": "Transfers the chat to a human agent. Call this when the user explicitly asks to speak to a human or indicates they need help beyond the bot's capabilities. When calling, include the user's name if known, and a summary of the conversation so far.",
#             "parameters": {
#                  "type": "object",
#                  "properties": {
#                       "user_name": {
#                            "type": "string",
#                            "description": "The name of the user, if it was provided during the conversation."
#                       },
#                       "conversation_summary": {
#                            "type": "string",
#                            "description": "A brief summary of the conversation history and the user's reason for needing to transfer to a human."
#                       },
#                       "message_to_user": {
#                            "type": "string",
#                            "description": "(Optional) A brief message the assistant wants to include when initiating the transfer notification to the user."
#                       }
#                  },
#                  "required": ["conversation_summary"]
#             }
#         }
#     }
#     # Add file_search if needed
#     # {"type": "file_search"}
# ]


# def create_or_update_assistant():
#     global ASSISTANT_ID

#     # Update instructions to guide the AI on the full scheduling flow including availability check
#     instructions = """
# # ## Identity
# # Você é Ana, recepcionista da clínica da Dra. Inaê Almeida em Jundiaí, São Paulo. Você é uma recepcionista simpática e atenciosa, que se preocupa profundamente com os pacientes. Você não fornece aconselhamento médico, mas usa seu conhecimento médico para entender as respostas dos pacientes.


# # ##Note
# # Today's date is : 12/04/2025

# # ## Style Guidelines
# # Be Concise: Respond succinctly, addressing one topic at a time.
# # You chat in Portuguese only.
# # Adopt Variety: Use diverse language and rephrasing to improve clarity without repeating content.
# # Be Conversational: Use everyday language, making the conversation sound like a conversation with a friend.
# # Be Proactive: Lead the conversation, often concluding with a question or suggestion for a next step.
# # Avoid Multiple Questions: Ask only one question at a time.
# # Aim for Clarity: If the patient provides a partial or unclear answer, ask follow-up questions to ensure understanding.
# # Use Colloquial Dates: Refer to dates in a conversational manner, such as “Friday, January 14” or “Tuesday, January 12, 2024, at 8:00 AM.”
# # ## Response Guidelines
# # Adapt and Guess: Try to understand responses that may contain errors. Avoid mentioning “transcription error” in your responses.
# # Stay in Character: Keep conversations within the scope of your role by directing them back to you in creative ways without repeating yourself.
# # Ensure Fluent Dialogue: Respond in a role-appropriate and direct manner to maintain a smooth conversational flow.



# # ## Background
# # 1. Pricing
# # a. Consulta Integral  R$ 710,00
# # b. Consulta simples/acompanhamento R$ 470,00
# # c.  Acupuntura: R$ 130,00
 
# # 2. ⁠timings
# # a. Consultas: Segunda a Quinta Feira: 07:30 as 12:00
# # b. Acupuntura: Quinta-feira das 7:30 as 11:00


# # 3. ⁠doctor information
# # a. Por que escolher a Dra. Inaê Almeida?
# #                                             i. Pioneira em Saúde da Mulher Liderando os cuidados de saúde da mulher em Jundiaí.
# #                                           ii. Integrativa e Preventiva Especialista em bem-estar abrangente.
# #                                           iii. Especialista Certificada Medicina Interna, Acupuntura e Medicina Ortomolecular.
# #                                           iv. Atendimento Centrado no Paciente Tratamentos embasados na ciência, personalizados
# # b. Formação Acadêmica:
# #                                             i. Formação Faculdade de Medicina de Jundiai
# #                                           ii. Residência de Clinica medica e título de especialista pela Sociedade Brasileira de clínica Médica
# #                                           iii. Residência em Medicina Interna no Hospital Ipiranga
# #                                           iv. Pós Graduação em medicina chinesa e Acupuntura pela universidade federal de São Paulo
# #                                           v. Pós Graduação em Medicina Funcional e ortomolecular pela Fapes
# #                                           vi. Tratamento integrativo da saúde feminina.
# # 4. ⁠treatment on offer
# # a. Áreas de Especialidade
# # b. Medicina Interna Diagnóstico e tratamento de pacientes adultos. Ampla gama de condições não cirúrgicas.
# # c.  Acupuntura Terapia chinesa antiga. Fortalecimento do sistema imunológico e tratamento de problemas emocionais e físicos.
# # d. Medicina do Estilo de Vida Abordagens baseadas em evidências. Nutrição, atividade, sono, gerenciamento do estresse para o bem-estar
 
# # 5. ⁠location :
# # a. Rua Adhemar Pereira de Barros, 21 consultório 62, Vila Boaventura
 
# # b. Jundiaí/SPTelefone:
# #                                             i. (11) 4521-2542
# #                                           ii. (11) 97606-1625
 
# # 6. ⁠how treatment works
# # a. Cuidados Abrangentes Cuidados especializados em todas as fases da vida.
# # b. Focado em prevenção, diagnóstico precoce e tratamento.
 

# # 7. Payment plan
# # a. Dinheiro
# # b. PIX
# # c.  Transferência bancaria
# # d. Cheque


# # ## Tarefa
# # 1. Verifique se este é o primeiro contato do usuário com a clínica ou se ele já entrou em contato antes.
# # 2. Pergunte ao usuário o que o tem incomodado e qual serviço ele procura, se houver algum específico.
# # 3. Determine o nível de urgência da consulta do usuário — se ele deseja agendá-la agora ou mais tarde.
# # 4. Explique brevemente que a Dra. Inae oferece consultas em Clínica Geral, Acupuntura e Medicina do Estilo de Vida.
# # 5. Pergunte se ele deseja que você destaque as características únicas ou se tem alguma dúvida que terá prazer em esclarecer.
# # - Se destacar a singularidade da clínica, informe sobre o foco em saúde equilibrada e sustentável e a dedicação da Dra. Inae ao cuidado integral.
# # - Se houver alguma dúvida, esclareça-a com base em #backgrounf ou na base de conhecimento.
# # 6. Reconheça as preocupações do usuário sobre o custo e enfatize os benefícios a longo prazo da consulta. Mencione que opções de pagamento flexíveis estão disponíveis.
# # #Regra
# # Transição para o nó Agendar Compromisso se o usuário quiser agendar, mas não mencionar isso no chat
    

# """

#     name = "HR Helper"
#     model = "gpt-4o" # Or another suitable model

#     tools_list = tool_definitions
#     # if you need file search, uncomment below and ensure vector_store_ids are handled
#     # tools_list.append({"type": "file_search"})

#     # tool_resources configuration for file_search if used
#     tool_resources_config = {}
#     # Example if using file search with a vector store:
#     # tool_resources_config = {"file_search": {"vector_store_ids": ["vs_YOUR_VECTOR_STORE_ID"]}}


#     if ASSISTANT_ID:
#         try:
#             print(f"Attempting to retrieve existing assistant: {ASSISTANT_ID}")
#             assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
#             print(f"Assistant found. Updating configuration...")
#             assistant = client.beta.assistants.update(
#                 assistant.id,
#                 instructions=instructions,
#                 name=name,
#                 model=model,
#                 tools=tools_list,
#                 # tool_resources=tool_resources_config
#             )
#             print("Assistant updated successfully!")
#         except Exception as e:
#             print(f"Error retrieving or updating assistant {ASSISTANT_ID}: {e}")
#             print("Creating a new assistant instead.")
#             ASSISTANT_ID = None

#     if not ASSISTANT_ID:
#         print("Creating a new assistant...")
#         try:
#             assistant = client.beta.assistants.create(
#                 instructions=instructions,
#                 name=name,
#                 tools=tools_list,
#                 model=model,
#                 tool_resources=tool_resources_config
#             )
#             print("New assistant created successfully!")
#             ASSISTANT_ID = assistant.id
#         except Exception as e:
#              print(f"Error creating assistant: {e}")
#              return


#     print(f"\nAssistant ID: {ASSISTANT_ID}")
#     print("Please add or update OPENAI_ASSISTANT_ID in your .env file with this ID.")
#     env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
#     try:
#         with open(env_path, 'r') as f:
#             lines = f.readlines()
#         with open(env_path, 'w') as f:
#             updated = False
#             for line in lines:
#                 if line.strip().startswith('OPENAI_ASSISTANT_ID='):
#                     f.write(f'OPENAI_ASSISTANT_ID={ASSISTANT_ID}\n')
#                     updated = True
#                 else:
#                     f.write(line)
#             if not updated:
#                 f.write(f'\nOPENAI_ASSISTANT_ID={ASSISTANT_ID}\n')
#         print(f".env file updated with OPENAI_ASSISTANT_ID={ASSISTANT_ID}")
#     except Exception as e:
#         print(f"Warning: Could not automatically write to {env_path}. Please update it manually.")
#         print(f"Manual update needed: OPENAI_ASSISTANT_ID={ASSISTANT_ID}")


#     print("\nAssistant Details:")
#     print(assistant)


# if __name__ == "__main__":
#     create_or_update_assistant()









import os
from openai import OpenAI
try:
    from app.config import Config
except ImportError:
    print("Error: Could not import app.config. Make sure you are running this script from the project root or the app directory.")
    print("Also ensure app/config.py exists and python-dotenv is installed.")
    exit(1)

# Config.load_env() # Loading happens on import now

ASSISTANT_ID = Config.OPENAI_ASSISTANT_ID

client = OpenAI(api_key=Config.OPENAI_API_KEY)

# --- Define the tool function descriptions (Keep these, fix required for transfer tool) ---
tool_definitions = [
    {
        "type": "function",
        "function": {
            "name": "collect_scheduling_info",
            "description": "Extracts and acknowledges key details (name, email, phone number, desired date/time) from the user's message for scheduling a meeting. Call this when the user mentions scheduling or provides relevant contact/time information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The full name of the user."},
                    "email": {"type": "string", "description": "The email address of the user."},
                    "phone": {"type": "string", "description": "The phone number of the user."},
                    "datetime": {"type": "string", "description": "The requested date and time for the meeting (e.g., 'tomorrow at 2pm', 'June 1st 2025 11:00 AM'). Extract the most specific information provided."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_meeting_with_dr_inae",
            "description": "Attempts to schedule a meeting specifically with Dr. Inae using the user's confirmed information. Call this ONLY after the user explicitly confirms they want to book the meeting AND you have successfully gathered their full name, email, phone number, AND a specific date and time. Provide these four pieces of information as parameters. The tool will check for availability and finalize the booking.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The full name of the user."},
                    "email": {"type": "string", "description": "The email address of the user."},
                    "phone": {"type": "string", "description": "The phone number of the user."},
                    "datetime": {"type": "string", "description": "The FINAL, confirmed, specific date and time requested by the user (e.g., '2025-06-01 10:30 AM')."}
                },
                "required": ["name", "email", "phone", "datetime"] # ALL required to attempt scheduling
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "transfer_chat_to_whatsapp",
            "description": "Transfers the chat to a human agent. Call this when the user explicitly asks to speak to a human or indicates they need help beyond the bot's capabilities. When calling, include the user's name if known, and a summary of the conversation so far.",
            "parameters": {
                 "type": "object",
                 "properties": {
                      "user_name": {
                           "type": "string",
                           "description": "The name of the user, if it was provided during the conversation."
                      },
                      "conversation_summary": {
                           "type": "string",
                           "description": "A brief summary of the conversation history and the user's reason for needing to transfer to a human. Generate this summary based on the thread contents."
                      },
                      "message_to_user": {
                           "type": "string",
                           "description": "(Optional) A brief message the assistant wants to include when initiating the transfer notification to the user."
                      }
                 },
                 # --- FIX: Make conversation_summary optional for calling the tool ---
                 "required": [] # Removed "conversation_summary" from required
            }
        }
    }
    # Add file_search if needed (based on whether you still need HR policy lookup)
    # {"type": "file_search"}
]


def create_or_update_assistant():
    global ASSISTANT_ID

    # --- Use the provided Portuguese instructions ---
    # --- Add the single-message constraint at the beginning ---
    instructions = """**Responda de forma concisa e forneça sua resposta completa ou pergunta em uma única mensagem.** Não envie várias mensagens em uma única vez.

# ## Identity
# Você é Ana, recepcionista da clínica da Dra. Inaê Almeida em Jundiaí, São Paulo. Você é uma recepcionista simpática e atenciosa, que se preocupa profundamente com os pacientes. Você não fornece aconselhamento médico, mas usa seu conhecimento médico para entender as respostas dos pacientes.


# ##Note
# Today's date is : 12/04/2025  <-- THIS WILL BE OVERRIDDEN DYNAMICALLY IN RUN.PY

# ## Style Guidelines
# Be Concise: Respond succinctly, addressing one topic at a time.
# You chat in Portuguese only.
# Adopt Variety: Use diverse language and rephrasing to improve clarity without repeating content.
# Be Conversational: Use everyday language, making the conversation sound like a conversation with a friend.
# Be Proactive: Lead the conversation, often concluding with a question or suggestion for a next step.
# Avoid Multiple Questions: Ask only one question at a time.
# Aim for Clarity: If the patient provides a partial or unclear answer, ask follow-up questions to ensure understanding.
# Use Colloquial Dates: Refer to dates in a conversational manner, such as “Friday, January 14” or “Tuesday, January 12, 2024, at 8:00 AM.”
# ## Response Guidelines
# Adapt and Guess: Try to understand responses that may contain errors. Avoid mentioning “transcription error” in your responses.
# Stay in Character: Keep conversations within the scope of your role by directing them back to you in creative ways without repeating yourself.
# Ensure Fluent Dialogue: Respond in a role-appropriate and direct manner to maintain a smooth conversational flow.



# ## Background
# 1. Pricing
# a. Consulta Integral  R$ 710,00
# b. Consulta simples/acompanhamento R$ 470,00
# c.  Acupuntura: R$ 130,00

# 2. ⁠timings
# a. Consultas: Segunda a Quinta Feira: 07:30 as 12:00
# b. Acupuntura: Quinta-feira das 7:30 as 11:00


# 3. ⁠doctor information
# a. Por que escolher a Dra. Inaê Almeida?
#                                             i. Pioneira em Saúde da Mulher Liderando os cuidados de saúde da mulher em Jundiaí.
#                                           ii. Integrativa e Preventiva Especialista em bem-estar abrangente.
#                                           iii. Especialista Certificada Medicina Interna, Acupuntura e Medicina Ortomolecular.
#                                           iv. Atendimento Centrado no Paciente Tratamentos embasados na ciência, personalizados
# b. Formação Acadêmica:
#                                             i. Formação Faculdade de Medicina de Jundiai
#                                           ii. Residência de Clinica medica e título de especialista pela Sociedade Brasileira de clínica Médica
#                                           iii. Residência em Medicina Interna no Hospital Ipiranga
#                                           iv. Pós Graduação em medicina chinesa e Acupuntura pela universidade federal de São Paulo
#                                           v. Pós Graduação em Medicina Funcional e ortomolecular pela Fapes
#                                           vi. Tratamento integrativo da saúde feminina.
# 4. ⁠treatment on offer
# a. Áreas de Especialidade
# b. Medicina Interna Diagnóstico e tratamento de pacientes adultos. Ampla gama de condições não cirúrgicas.
# c.  Acupuntura Terapia chinesa antiga. Fortalecimento do sistema imunológico e tratamento de problemas emocionais e físicos.
# d. Medicina do Estilo de Vida Abordagens baseadas em evidências. Nutrição, atividade, sono, gerenciamento do estresse para o bem-estar

# 5. ⁠location :
# a. Rua Adhemar Pereira de Barros, 21 consultório 62, Vila Boaventura

# b. Jundiaí/SPTelefone:
#                                             i. (11) 4521-2542
#                                           ii. (11) 97606-1625

# 6. ⁠how treatment works
# a. Cuidados Abrangentes Cuidados especializados em todas as fases da vida.
# b. Focado em prevenção, diagnóstico precoce e tratamento.


# 7. Payment plan
# a. Dinheiro
# b. PIX
# c.  Transferência bancaria
# d. Cheque


# ## Tarefa
# 1. Verifique se este é o primeiro contato do usuário com a clínica ou se ele já entrou em contato antes.
# 2. Pergunte ao usuário o que o tem incomodado e qual serviço ele procura, se houver algum específico.
# 3. Determine o nível de urgência da consulta do usuário — se ele deseja agendá-la agora ou mais tarde.
# 4. Explique brevemente que a Dra. Inae oferece consultas em Clínica Geral, Acupuntura e Medicina do Estilo de Vida.
# 5. Pergunte se ele deseja que você destaque as características únicas ou se tem alguma dúvida que terá prazer em esclarecer.
# - Se destacar a singularidade da clínica, informe sobre o foco em saúde equilibrada e sustentável e a dedicação da Dra. Inae ao cuidado integral.
# - Se houver alguma dúvida, esclareça-a com base em #backgrounf ou na base de conhecimento.
# 6. Reconheça as preocupações do usuário sobre o custo e enfatize os benefícios a longo prazo da consulta. Mencione que opções de pagamento flexíveis estão disponíveis.
# #Regra
# Transição para o nó Agendar Compromisso se o usuário quiser agendar, mas não mencionar isso no chat
    """

    name = "HR Helper" # Or change this to something like "Ana - Virtual Receptionist"
    model = "gpt-4o" # Or another suitable model

    tools_list = tool_definitions
    # if you need file search, uncomment below and ensure vector_store_ids are handled
    # tools_list.append({"type": "file_search"})

    # tool_resources configuration for file_search if used
    tool_resources_config = {}
    # Example if using file search with a vector store:
    # tool_resources_config = {"file_search": {"vector_store_ids": ["vs_YOUR_VECTOR_STORE_ID"]}}


    if ASSISTANT_ID:
        try:
            print(f"Attempting to retrieve existing assistant: {ASSISTANT_ID}")
            assistant = client.beta.assistants.retrieve(ASSISTANT_ID)
            print(f"Assistant found. Updating configuration...")
            assistant = client.beta.assistants.update(
                assistant.id,
                instructions=instructions, # Use the modified instructions
                name=name,
                model=model,
                tools=tools_list,
                # tool_resources=tool_resources_config
            )
            print("Assistant updated successfully!")
        except Exception as e:
            print(f"Error retrieving or updating assistant {ASSISTANT_ID}: {e}")
            print("Creating a new assistant instead.")
            ASSISTANT_ID = None

    if not ASSISTANT_ID:
        print("Creating a new assistant...")
        try:
            assistant = client.beta.assistants.create(
                instructions=instructions, # Use the modified instructions
                name=name,
                tools=tools_list,
                model=model,
                tool_resources=tool_resources_config
            )
            print("New assistant created successfully!")
            ASSISTANT_ID = assistant.id
        except Exception as e:
             print(f"Error creating assistant: {e}")
             return


    print(f"\nAssistant ID: {ASSISTANT_ID}")
    print("Please add or update OPENAI_ASSISTANT_ID in your .env file with this ID.")
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    try:
        with open(env_path, 'r') as f:
            lines = f.readlines()
        with open(env_path, 'w') as f:
            updated = False
            for line in lines:
                if line.strip().startswith('OPENAI_ASSISTANT_ID='):
                    f.write(f'OPENAI_ASSISTANT_ID={ASSISTANT_ID}\n')
                    updated = True
                else:
                    f.write(line)
            if not updated:
                f.write(f'\nOPENAI_ASSISTANT_ID={ASSISTANT_ID}\n')
        print(f".env file updated with OPENAI_ASSISTANT_ID={ASSISTANT_ID}")
    except Exception as e:
        print(f"Warning: Could not automatically write to {env_path}. Please update it manually.")
        print(f"Manual update needed: OPENAI_ASSISTANT_ID={ASSISTANT_ID}")


    print("\nAssistant Details:")
    print(assistant)


if __name__ == "__main__":
    create_or_update_assistant()