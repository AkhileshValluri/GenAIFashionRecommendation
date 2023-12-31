import guardrails as gd
import openai 
import os
class Chatbot(): 
    def __init__(self): 
        """Preprocessing embeddings.txt file to get all unique categories"""

        # Define the attributes for which you want to find unique categories
        attributes = ['gender', 'masterCategory', 'subCategory', 'articleType', 'baseColour', 'season', 'usage']

        # Read the content of the embeddings.txt file
        with open('embeddings.txt', 'r') as file:
            content = file.read()

        # Split content into individual product entries
        products = content.strip().split('\n\n')

        # Initialize dictionaries to store unique categories for each attribute
        unique_categories = {attr: set() for attr in attributes}

        # Process each product entry and extract unique categories
        for product in products:
            lines = product.strip().split('\n')
            product_data = {}
            for line in lines:
                key, value = line.split(' : ', 1)
                product_data[key] = value.strip()

            # Extract unique categories for each attribute
            for attr in attributes:
                if attr in product_data:
                    unique_categories[attr].add(product_data[attr])

        # Print the unique categories for each attribute
        self.unique_categories = unique_categories
        self.attributes = attributes
    
    def get_guardrail_instance(self, metadata = "", messages = ""): 
        category_string_to_attr = {attr : str() for attr in self.attributes}
        for attr in self.attributes : 
            unique_cat = self.unique_categories[attr]
            cat_string = "valid-choices : {["
            for cat in unique_cat: 
                cat_string += f"'{cat}', "
            cat_string = cat_string[:len(cat_string) - 2]
            cat_string += ']}'
            category_string_to_attr[attr] = cat_string
        
        messages = messages[:3] # only last 3 messages
        # for attr in category_string_to_attr.keys(): 
        #     print(attr, category_string_to_attr[attr])
        rail_spec = f"""
            <rail version = "0.1"> 
                <output> 
                    <string name = "response"
                        description = "Response to the user Query"
                    />
                    <string name = "gender" 
                        description = "Gender or sex of person identified through metadata or prompt"
                        format = "{category_string_to_attr['gender']}; multiple-matches"
                    />
                    <string name = "articleType" 
                        description = "Clothing articles that were mentioned in the most recent prompt. If info isn't given, then search previous prompts"
                        format = "{category_string_to_attr['articleType']}; multiple-matches"
                    />
                    <string name = "baseColour" 
                        description = "Colour of clothing article mentioned in most recent prompt"
                    />
                    <string name = "brand" 
                        description = "Brand of article user mentioned in the most recent prompt"
                    />
                    <string name = "season" 
                        description = "Season of clothing article"
                    />
                </output>

                <prompt>
                    You are a classifier who should extract information from the query history of a user and respond to user. 
                    Most recent prompt is given in the last.
                    You can return multiple categories if you feel like they are similar enough or if user hasn't mentioned anything specific.
                    In the response be friendly and helpful. Respond to tell what you understood from their query.
                    USER QUERY HISTORY: 
                    {{{{user_query}}}}
                    METADATA:
                    {{{{metadata}}}}
                    @complete_json_suffix_v2
                </prompt>
            </rail>
        """
        
        guard = gd.Guard.from_rail_string(rail_string=rail_spec)
        return guard
    
    def _make_openai_query(self, guard, messages, metadata): 
        """Makes the acutal open AI call, returns the vector DB queryable string"""
        import dotenv
        dotenv.load_dotenv()
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        raw_llm_output, validated_output = guard(
            openai.Completion.create, 
            engine = 'text-davinci-003', 
            max_tokens = 256, 
            prompt_params = {'user_query' : messages, 'metadata' : metadata}, 
            temperature = 0.1
        )
        return validated_output
    
    def get_chatbot_reply(self, messages, metadata): 
        guard = self.get_guardrail_instance(messages = messages, metadata=metadata)
        return self._make_openai_query(guard, messages, metadata)

