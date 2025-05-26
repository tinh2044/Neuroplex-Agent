import json
import os
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    AutoConfig,
    GenerationConfig,
    BitsAndBytesConfig
)
from ai_engine.utils import logger
import dotenv

dotenv.load_dotenv()

class KnowledgeExtractorProcessor:
    """
    Advanced knowledge extraction system using transformer models
    for processing text and generating structured knowledge graphs
    """
    
    # Template configurations for different extraction modes
    EXTRACTION_TEMPLATES = {
        "entity_extraction_en": "As an information mining specialist, identify and extract {target_schema} from the provided text:\nContent: {source_text}",
        "relationship_mining_en": "As a relationship analysis expert, discover {target_schema} connections within the text:\nContent: {source_text}",
        "knowledge_synthesis_en": "As a knowledge graph architect, synthesize {target_schema} information from the text in JSON structure:\nContent: {source_text}",
        "entity_extraction_vi": "Với vai trò chuyên gia phân tích dữ liệu, hãy nhận diện và trích xuất {target_schema} từ nội dung:\nNội dung: {source_text}",
        "relationship_mining_vi": "Với vai trò chuyên gia phân tích mối quan hệ, hãy khám phá các kết nối {target_schema} trong văn bản:\nNội dung: {source_text}",
        "knowledge_synthesis_vi": "Với vai trò kiến trúc sư tri thức, hãy tổng hợp thông tin {target_schema} từ văn bản và trả về JSON:\nNội dung: {source_text}"
    }
    
    # Batch processing limits for different operations
    BATCH_PROCESSING_LIMITS = {
        "entity_extraction": 6,
        "relationship_mining": 4,
        "knowledge_synthesis": 1
    }
    
    def __init__(self, model_repository="zjunlp/OneKE"):
        """Initialize the knowledge mining system with specified model"""
        self.compute_device = "cuda" if torch.cuda.is_available() else "cpu"
        self._initialize_model_components(model_repository)
        
    def _initialize_model_components(self, model_repo):
        """Setup model, tokenizer and generation configuration"""
        # Configure 4-bit quantization for memory efficiency
        quantization_setup = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
        
        # Initialize model components
        self.text_processor = AutoTokenizer.from_pretrained(
            model_repo, 
            use_fast=False, 
            trust_remote_code=True
        )
        
        self.neural_model = AutoModelForCausalLM.from_pretrained(
            model_repo,
            config=AutoConfig.from_pretrained(model_repo),
            quantization_config=quantization_setup,
            device_map="auto",
            trust_remote_code=True
        )
        
        self.generation_parameters = GenerationConfig.from_pretrained(model_repo)
        self.neural_model.eval()
    
    def _prepare_extraction_prompts(self, content, schema_definition, operation_type, lang_code="zh", enable_batching=False):
        """Prepare structured prompts for knowledge extraction"""
        if enable_batching:
            batch_size = self.BATCH_PROCESSING_LIMITS[operation_type]
            if isinstance(schema_definition, dict):
                schema_chunks = list(schema_definition.keys())
                schema_batches = [schema_chunks[i:i+batch_size] for i in range(0, len(schema_chunks), batch_size)]
                processed_schemas = [{key: schema_definition[key] for key in batch} for batch in schema_batches]
            else:
                processed_schemas = [schema_definition[i:i+batch_size] for i in range(0, len(schema_definition), batch_size)]
        else:
            processed_schemas = [schema_definition]
        
        prompt_instructions = []
        template_key = f"{operation_type}_{lang_code}"
        
        for schema_chunk in processed_schemas:
            instruction_data = json.dumps({
                "instruction": self.EXTRACTION_TEMPLATES[template_key],
                "target_schema": schema_chunk,
                "source_text": content,
            }, ensure_ascii=False)
            prompt_instructions.append(instruction_data)
        
        return prompt_instructions
    
    def execute_knowledge_extraction(self, content, schema_definition, operation_type, lang_code="zh", enable_batching=False):
        """Execute knowledge extraction using the neural model"""
        prepared_prompts = self._prepare_extraction_prompts(
            content, schema_definition, operation_type, lang_code, enable_batching
        )
        
        extraction_results = []
        
        for prompt in prepared_prompts:
            # Tokenize and prepare input
            tokenized_input = self.text_processor.encode(prompt, return_tensors="pt").to(self.neural_model.device)
            original_length = tokenized_input.size(1)
            
            # Generate response
            model_output = self.neural_model.generate(
                input_ids=tokenized_input,
                generation_config=self.generation_parameters,
                pad_token_id=self.text_processor.eos_token_id
            )
            
            # Extract generated content
            generated_sequence = model_output.sequences[0]
            new_tokens = generated_sequence[original_length:]
            decoded_result = self.text_processor.decode(new_tokens, skip_special_tokens=True)
            
            extraction_results.append(decoded_result)
        
        return extraction_results
    
    def transform_text_to_knowledge_graph(self, input_source, destination_file):
        """Transform text content into structured knowledge graph format"""
        for text_segment in self._stream_text_chunks(input_source):
            content = text_segment
            
            # Define food knowledge schema
            food_knowledge_schema = [
                {
                    "entity_type": "Food",
                    "attributes": {
                        "Name": "The name of the food, including brand name, common name, or specialized chemical name",
                        "Category": "The type of food, such as fruit, vegetable, meat, grain, seasoning, additive, probiotic, etc.",
                        "Ingredients": "The main ingredients of the food, listing in detail including natural ingredients, additives, preservatives, nutritional fortifiers, etc.",
                        "Nutritional Value": "The nutritional components of the food, summarizing the energy provided and main nutrients such as protein, fat, carbohydrates, vitamins, and minerals",
                        "Processing Method": "The processing or preparation method of the food, including daily cooking, processing, and laboratory preparation methods, etc.",
                        "Effect or Consumption Outcome": "The impact of the food on health or the body, possible effects or uses"
                    }
                }
            ]
            
            operation = "knowledge_synthesis"
            raw_output = self.execute_knowledge_extraction(
                content=content, 
                schema_definition=food_knowledge_schema, 
                operation_type=operation, 
                lang_code="zh"
            )
            
            structured_results = self._convert_output_to_structured_format(
                raw_results=raw_output, 
                operation_mode=operation
            )
            
            # Append results to output file
            with open(destination_file, 'a+', encoding='utf-8') as output_file:
                for result_entry in structured_results:
                    output_file.write(json.dumps(result_entry, ensure_ascii=False) + '\n')
        
        print(f"Knowledge extraction completed. Results saved to {destination_file}")
        return destination_file

    def _stream_text_chunks(self, file_source, chunk_length=512, overlap_buffer=100):
        """Stream text in overlapping chunks for processing"""
        text_buffer = ""
        
        with open(file_source, 'r', encoding='utf-8') as input_file:
            while True:
                data_chunk = input_file.read(chunk_length)
                if not data_chunk:  # End of file reached
                    if text_buffer:
                        yield text_buffer
                    break
                
                # Clean the chunk
                cleaned_chunk = data_chunk.replace('\n', '').replace('\r', '')
                text_buffer += cleaned_chunk
                
                # Yield complete chunks with overlap
                while len(text_buffer) >= chunk_length:
                    yield text_buffer[:chunk_length]
                    text_buffer = text_buffer[chunk_length - overlap_buffer:]

    def _convert_output_to_structured_format(self, raw_results, operation_mode):
        """Convert raw model output to structured format"""
        structured_data = []
        
        for result_item in raw_results:
            try:
                # Validate JSON format
                if isinstance(result_item, str) and result_item.strip().startswith('{') and result_item.strip().endswith('}'):
                    parsed_data = json.loads(result_item)
                    
                    if operation_mode == "knowledge_synthesis":
                        # Process knowledge graph format
                        for entity_category, entity_instances in parsed_data.items():
                            for entity_id, entity_properties in entity_instances.items():
                                for property_name, property_values in entity_properties.items():
                                    if isinstance(property_values, list):
                                        for value_item in property_values:
                                            structured_data.append({
                                                "h": entity_id,
                                                "t": value_item,
                                                "r": property_name
                                            })
                                    else:
                                        structured_data.append({
                                            "h": entity_id,
                                            "t": property_values,
                                            "r": property_name
                                        })
                    
                    elif operation_mode == "relationship_mining":
                        # Process relationship format
                        for relation_category, relation_pairs in parsed_data.items():
                            for pair_data in relation_pairs:
                                structured_data.append({
                                    "h": pair_data["subject"],
                                    "t": pair_data["object"],
                                    "r": relation_category
                                })
                else:
                    raise json.JSONDecodeError("Invalid JSON structure", result_item, 0)
                
            except json.JSONDecodeError as json_error:
                print(f"JSON parsing error: {json_error} - Skipping invalid entry")
                continue
            except TypeError as type_error:
                print(f"Type error: {type_error} - Skipping malformed entry")
                continue
            except AttributeError as attr_error:
                print(f"Attribute error: {attr_error} - Skipping incomplete entry")
                continue
        
        return structured_data


if __name__ == "__main__":
    pass