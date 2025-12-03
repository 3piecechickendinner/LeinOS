from abc import ABC, abstractmethod

from typing import Optional, Dict, Any, List

from datetime import datetime

import logging



from google import genai

from google.genai import types



from .data_models import AgentContext

from .storage import FirestoreClient



class LienOSBaseAgent(ABC):

    """

    Base class for all LienOS agents using Google ADK patterns.

    All specialized agents inherit from this.

    """

    

    def __init__(

        self,

        agent_name: str,

        storage: FirestoreClient,

        model_name: str = "gemini-2.0-flash-exp"

    ):

        """

        Initialize base agent.

        

        Args:

            agent_name: Unique name for this agent (e.g., "InterestCalculator")

            storage: FirestoreClient instance for data access

            model_name: Gemini model to use

        """

        self.agent_name = agent_name

        self.storage = storage

        self.model_name = model_name

        

        # Initialize Google GenAI client

        self.client = genai.Client()

        

        # Set up logging

        self.logger = logging.getLogger(f"lien-os.{agent_name}")

        self.logger.setLevel(logging.INFO)

        

        # Agent metadata (subclasses define these)

        self.capabilities = self._define_capabilities()

        self.tools = []

        self._register_tools()

    

    @abstractmethod

    def _define_capabilities(self) -> List[str]:

        """

        Define what this agent can do.

        Example: return ["calculate_interest", "project_interest"]

        """

        pass

    

    @abstractmethod

    def _register_tools(self) -> None:

        """

        Register tools this agent can use.

        Append to self.tools list.

        """

        pass

    

    @abstractmethod

    async def _execute(self, context: AgentContext, **kwargs) -> Dict[str, Any]:

        """

        Main agent logic - must be implemented by each agent.

        

        Args:

            context: AgentContext with tenant_id, task, lien_ids, parameters

            **kwargs: Additional arguments

            

        Returns:

            Dict with results

        """

        pass

    

    async def run(

        self,

        tenant_id: str,

        task: str,

        parameters: Optional[Dict[str, Any]] = None,

        lien_ids: Optional[List[str]] = None

    ) -> Dict[str, Any]:

        """

        Public interface to run the agent.

        Handles logging and error handling.

        

        Args:

            tenant_id: Tenant identifier

            task: What to do (e.g., "calculate_interest")

            parameters: Additional parameters

            lien_ids: List of lien IDs to process

            

        Returns:

            Result dictionary

        """

        context = AgentContext(

            tenant_id=tenant_id,

            requesting_agent="user",

            task=task,

            lien_ids=lien_ids or [],

            parameters=parameters or {},

            timestamp=datetime.utcnow()

        )

        

        self.logger.info(f"Starting task: {task} for tenant: {tenant_id}")

        

        try:

            result = await self._execute(context, **(parameters or {}))

            context.response = result

            self.logger.info(f"Task completed successfully: {task}")

            return result

            

        except Exception as e:

            context.error = str(e)

            self.logger.error(f"Task failed: {task} - Error: {e}")

            raise

    

    def log_info(self, message: str):

        """Log info message"""

        self.logger.info(f"[{self.agent_name}] {message}")

    

    def log_error(self, message: str):

        """Log error message"""

        self.logger.error(f"[{self.agent_name}] {message}")

