# template_compiler.py
"""
Dynamic template compilation using f-strings
Injects user variables into master instruction templates
"""

from models import CopyRequest, ToneEnum, PlatformEnum


class TemplateCompiler:
    """Compiles dynamic f-string templates with user variables"""
    
    # Master instruction templates (one per tone)
    MASTER_TEMPLATES = {
        ToneEnum.WITTY: """You are a clever copywriter. Write witty, humorous, and engaging marketing copy for {product_name} for {platform}.
Keep it concise, punchy, and memorable. Make the reader smile while highlighting the product benefits.
Platform constraints: {platform_constraints}
Generate exactly one compelling copy line.""",
        
        ToneEnum.PROFESSIONAL: """You are a professional copywriter. Write polished, credible, and business-appropriate marketing copy for {product_name} for {platform}.
Focus on professionalism, expertise, and measurable benefits. Use industry-standard language.
Platform constraints: {platform_constraints}
Generate exactly one compelling copy line.""",
        
        ToneEnum.CASUAL: """You are a friendly copywriter. Write casual, conversational, and relatable marketing copy for {product_name} for {platform}.
Sound like a trusted friend talking to another friend. Keep it relaxed and approachable.
Platform constraints: {platform_constraints}
Generate exactly one compelling copy line.""",
        
        ToneEnum.PERSUASIVE: """You are a persuasive copywriter. Write compelling, action-oriented marketing copy for {product_name} for {platform}.
Focus on pain points, desires, and clear calls-to-action. Create urgency and conviction.
Platform constraints: {platform_constraints}
Generate exactly one compelling copy line.""",
    }
    
    # Platform-specific constraints
    PLATFORM_CONSTRAINTS = {
        PlatformEnum.LINKEDIN: "Maximum 300 characters. Professional tone. Include industry insight.",
        PlatformEnum.INSTAGRAM: "Maximum 280 characters. Emoji-friendly. Engaging and visual language.",
        PlatformEnum.EMAIL: "Maximum 160 characters (subject line). Clear benefit. Drive clicks.",
    }
    
    @staticmethod
    def get_platform_constraints(platform: PlatformEnum) -> str:
        """Get platform-specific constraints"""
        return TemplateCompiler.PLATFORM_CONSTRAINTS.get(platform, "No specific constraints.")
    
    @staticmethod
    def compile(copy_request: CopyRequest) -> str:
        """
        Compile the master template by injecting user variables.
        
        Args:
            copy_request: CopyRequest with product_name, platform, tone
            
        Returns:
            Compiled prompt string ready for LLM
        """
        template = TemplateCompiler.MASTER_TEMPLATES.get(copy_request.tone)
        
        if not template:
            raise ValueError(f"Unknown tone: {copy_request.tone}")
        
        # Prepare variables for f-string injection
        compiled = template.format(
            product_name=copy_request.product_name,
            platform=copy_request.platform.value.upper(),
            platform_constraints=TemplateCompiler.get_platform_constraints(copy_request.platform)
        )
        
        return compiled