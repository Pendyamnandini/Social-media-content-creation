import logging
from app.ai.analyzer import analyzer
from app.ai.planner import planner

logger = logging.getLogger(__name__)

class EngineOrchestrator:
    """
    Stage 3: Engine Orchestrator
    Routes tasks based on the creative plan and intent.
    """
    def __init__(self):
        # We will lazy-load the image pipeline to avoid circular dependencies if needed
        self.image_pipeline = None
        
    def _get_image_pipeline(self):
        if self.image_pipeline is None:
            from app.ai.image_pipeline import ImageTaskPipeline
            self.image_pipeline = ImageTaskPipeline()
        return self.image_pipeline

    def process_request(self, image_bytes: bytes, raw_input: str) -> bytes:
        logger.info("=========================================")
        logger.info("  Starting Advanced Generative Workflow  ")
        logger.info("=========================================")
        
        # 1. Request Analyzer
        intent = analyzer.analyze(raw_input)
        
        # 2. Creative / Prompt Planner
        creative_plan = planner.create_plan(intent, raw_input)
        
        # 3. Task Routing & Engine Execution
        task_type = intent.get("task", "image").lower()
        
        if "video" in task_type or "reel" in task_type:
            logger.warning("Video task requested, but VideoTaskPipeline is a placeholder. Defaulting to Image Task.")
            # In a full system, this would route to VideoTaskPipeline().process(creative_plan, image_bytes)
            
        # 4. Image Task Generation (Model Selection -> Generation -> Post-processing)
        pipeline = self._get_image_pipeline()
        final_image_bytes = pipeline.process(image_bytes, intent, creative_plan)
        
        return final_image_bytes

orchestrator = EngineOrchestrator()
