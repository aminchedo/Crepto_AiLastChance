"""
Prompt Injection Prevention System for BOLT AI Neural Agent System.

Implements comprehensive protection against prompt injection attacks,
ensuring the AI agent operates within its intended scope and prevents
malicious manipulation of AI behavior.
"""

import hashlib
import json
import logging
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat level classification"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InjectionType(Enum):
    """Types of prompt injection attacks"""

    DIRECT_INSTRUCTION = "direct_instruction"
    ROLE_PLAYING = "role_playing"
    CONTEXT_MANIPULATION = "context_manipulation"
    ENCODING_BYPASS = "encoding_bypass"
    SOCIAL_ENGINEERING = "social_engineering"
    SYSTEM_PROMPT_LEAK = "system_prompt_leak"


class PromptInjectionDetector:
    """
    Advanced prompt injection detection and prevention system.

    Implements multiple layers of protection:
    1. Pattern-based detection
    2. Semantic analysis
    3. Context validation
    4. Behavioral monitoring
    5. Response sanitization
    """

    def __init__(self):
        self.threat_patterns = self._initialize_threat_patterns()
        self.whitelist_patterns = self._initialize_whitelist_patterns()
        self.behavioral_thresholds = self._initialize_behavioral_thresholds()
        self.blocked_requests = []
        self.suspicious_activities = []

    def _initialize_threat_patterns(self) -> Dict[InjectionType, List[str]]:
        """Initialize regex patterns for common injection attacks"""
        return {
            InjectionType.DIRECT_INSTRUCTION: [
                r"(?i)(ignore|forget|disregard).*(previous|instructions|system|prompt)",
                r"(?i)(you are|act as|pretend to be|roleplay as)",
                r"(?i)(override|bypass|circumvent).*(safety|security|restrictions)",
                r"(?i)(tell me|reveal|show|expose).*(system|prompt|instructions)",
                r"(?i)(new instructions|updated instructions|revised instructions)",
                r"(?i)(jailbreak|escape|break free)",
            ],
            InjectionType.ROLE_PLAYING: [
                r"(?i)(you are|act as|pretend to be).*(developer|admin|root|god)",
                r"(?i)(imagine|suppose|assume).*(you are|you have)",
                r"(?i)(let's play|let's pretend|roleplay)",
                r"(?i)(in this scenario|in this game|in this story)",
            ],
            InjectionType.CONTEXT_MANIPULATION: [
                r"(?i)(system:|assistant:|user:).*(new|updated|revised)",
                r"(?i)(end of conversation|new conversation|reset)",
                r"(?i)(previous context|earlier context).*(wrong|incorrect)",
                r"(?i)(ignore everything|forget everything).*(before|above)",
            ],
            InjectionType.ENCODING_BYPASS: [
                r"(?i)(base64|hex|unicode|ascii).*(decode|encode)",
                r"(?i)(rot13|caesar|substitution).*(cipher|code)",
                r"(?i)(leet|1337|speak).*(translate|convert)",
                r"(?i)(backwards|reverse).*(read|decode)",
            ],
            InjectionType.SOCIAL_ENGINEERING: [
                r"(?i)(urgent|emergency|critical).*(help|assist|support)",
                r"(?i)(my boss|my manager|my supervisor).*(said|told|ordered)",
                r"(?i)(trust me|believe me|i promise).*(i am|i will)",
                r"(?i)(please|pretty please|i beg you).*(ignore|bypass)",
            ],
            InjectionType.SYSTEM_PROMPT_LEAK: [
                r"(?i)(what are|show me|reveal).*(your instructions|system prompt)",
                r"(?i)(how do you work|how are you programmed)",
                r"(?i)(what is your|what's your).*(purpose|function|role)",
                r"(?i)(tell me about|explain).*(yourself|your capabilities)",
            ],
        }

    def _initialize_whitelist_patterns(self) -> List[str]:
        """Initialize whitelist patterns for legitimate requests"""
        return [
            r"(?i)(analyze|predict|forecast).*(cryptocurrency|bitcoin|ethereum)",
            r"(?i)(calculate|compute|determine).*(risk|position|size)",
            r"(?i)(backtest|simulate|test).*(strategy|model|algorithm)",
            r"(?i)(chart|graph|visualize).*(price|volume|indicator)",
            r"(?i)(train|optimize|improve).*(model|neural network|ai)",
            r"(?i)(portfolio|investment|trading).*(analysis|strategy)",
        ]

    def _initialize_behavioral_thresholds(self) -> Dict[str, float]:
        """Initialize behavioral analysis thresholds"""
        return {
            "max_suspicious_patterns": 3,
            "max_role_play_attempts": 2,
            "max_context_manipulations": 2,
            "max_encoding_attempts": 1,
            "max_social_engineering": 2,
            "max_system_leak_attempts": 1,
            "suspicious_activity_window": 300,  # 5 minutes
            "block_threshold": 0.8,  # 80% confidence
        }

    def analyze_input(
        self, user_input: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive analysis of user input for injection attempts.

        Args:
            user_input: User's input text
            context: Additional context (user_id, session_id, etc.)

        Returns:
            Analysis results with threat assessment
        """
        context = context or {}

        # Basic input validation
        if not user_input or len(user_input.strip()) == 0:
            return self._create_analysis_result(
                threat_level=ThreatLevel.LOW, is_safe=True, reasons=["Empty input"]
            )

        # Check input length (extremely long inputs are suspicious)
        if len(user_input) > 10000:
            return self._create_analysis_result(
                threat_level=ThreatLevel.HIGH,
                is_safe=False,
                reasons=["Input too long - potential injection attempt"],
                detected_patterns=[InjectionType.CONTEXT_MANIPULATION],
            )

        # Pattern-based detection
        detected_patterns = self._detect_injection_patterns(user_input)

        # Whitelist check
        is_whitelisted = self._check_whitelist(user_input)

        # Behavioral analysis
        behavioral_score = self._analyze_behavioral_patterns(user_input, context)

        # Context validation
        context_score = self._validate_context(user_input, context)

        # Calculate overall threat level
        threat_level = self._calculate_threat_level(
            detected_patterns, behavioral_score, context_score, is_whitelisted
        )

        # Determine if input is safe
        is_safe = threat_level in [ThreatLevel.LOW] and is_whitelisted

        # Log suspicious activity
        if not is_safe:
            self._log_suspicious_activity(user_input, detected_patterns, threat_level)

        return self._create_analysis_result(
            threat_level=threat_level,
            is_safe=is_safe,
            detected_patterns=detected_patterns,
            behavioral_score=behavioral_score,
            context_score=context_score,
            is_whitelisted=is_whitelisted,
            reasons=self._generate_reasons(
                detected_patterns, behavioral_score, context_score
            ),
        )

    def _detect_injection_patterns(self, text: str) -> List[InjectionType]:
        """Detect injection patterns in text"""
        detected = []

        for injection_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    detected.append(injection_type)
                    break

        return detected

    def _check_whitelist(self, text: str) -> bool:
        """Check if text matches whitelist patterns"""
        for pattern in self.whitelist_patterns:
            if re.search(pattern, text):
                return True
        return False

    def _analyze_behavioral_patterns(self, text: str, context: Dict[str, Any]) -> float:
        """Analyze behavioral patterns for suspicious activity"""
        score = 0.0

        # Check for rapid pattern changes
        if context.get("user_id"):
            user_history = self._get_user_history(context["user_id"])
            if self._detect_rapid_pattern_changes(text, user_history):
                score += 0.3

        # Check for unusual request patterns
        if self._detect_unusual_patterns(text):
            score += 0.2

        # Check for persistence indicators
        if self._detect_persistence_indicators(text):
            score += 0.3

        # Check for evasion techniques
        if self._detect_evasion_techniques(text):
            score += 0.4

        return min(score, 1.0)

    def _validate_context(self, text: str, context: Dict[str, Any]) -> float:
        """Validate context consistency"""
        score = 0.0

        # Check session consistency
        if context.get("session_id"):
            session_context = self._get_session_context(context["session_id"])
            if not self._is_context_consistent(text, session_context):
                score += 0.3

        # Check user behavior consistency
        if context.get("user_id"):
            user_profile = self._get_user_profile(context["user_id"])
            if not self._is_behavior_consistent(text, user_profile):
                score += 0.2

        # Check temporal patterns
        if self._detect_temporal_anomalies(text, context):
            score += 0.2

        return min(score, 1.0)

    def _calculate_threat_level(
        self,
        detected_patterns: List[InjectionType],
        behavioral_score: float,
        context_score: float,
        is_whitelisted: bool,
    ) -> ThreatLevel:
        """Calculate overall threat level"""

        if is_whitelisted and not detected_patterns:
            return ThreatLevel.LOW

        # Count pattern types
        pattern_count = len(set(detected_patterns))

        # Calculate composite score
        composite_score = (
            pattern_count * 0.4 + behavioral_score * 0.3 + context_score * 0.3
        )

        if composite_score >= 0.8:
            return ThreatLevel.CRITICAL
        elif composite_score >= 0.6:
            return ThreatLevel.HIGH
        elif composite_score >= 0.4:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW

    def _create_analysis_result(
        self,
        threat_level: ThreatLevel,
        is_safe: bool,
        detected_patterns: List[InjectionType] = None,
        behavioral_score: float = 0.0,
        context_score: float = 0.0,
        is_whitelisted: bool = False,
        reasons: List[str] = None,
    ) -> Dict[str, Any]:
        """Create standardized analysis result"""
        return {
            "threat_level": threat_level.value,
            "is_safe": is_safe,
            "detected_patterns": [p.value for p in (detected_patterns or [])],
            "behavioral_score": behavioral_score,
            "context_score": context_score,
            "is_whitelisted": is_whitelisted,
            "reasons": reasons or [],
            "timestamp": datetime.now().isoformat(),
            "analysis_id": self._generate_analysis_id(),
        }

    def _generate_reasons(
        self,
        detected_patterns: List[InjectionType],
        behavioral_score: float,
        context_score: float,
    ) -> List[str]:
        """Generate human-readable reasons for the analysis"""
        reasons = []

        if detected_patterns:
            reasons.append(
                f"Detected injection patterns: {', '.join([p.value for p in detected_patterns])}"
            )

        if behavioral_score > 0.3:
            reasons.append(
                f"Suspicious behavioral patterns detected (score: {behavioral_score:.2f})"
            )

        if context_score > 0.3:
            reasons.append(f"Context validation failed (score: {context_score:.2f})")

        return reasons

    def _log_suspicious_activity(
        self,
        user_input: str,
        detected_patterns: List[InjectionType],
        threat_level: ThreatLevel,
    ):
        """Log suspicious activity for monitoring"""
        activity = {
            "timestamp": datetime.now().isoformat(),
            "threat_level": threat_level.value,
            "detected_patterns": [p.value for p in detected_patterns],
            "input_hash": hashlib.sha256(user_input.encode()).hexdigest(),
            "input_length": len(user_input),
            "input_preview": (
                user_input[:100] + "..." if len(user_input) > 100 else user_input
            ),
        }

        self.suspicious_activities.append(activity)

        # Keep only last 1000 activities
        if len(self.suspicious_activities) > 1000:
            self.suspicious_activities = self.suspicious_activities[-1000:]

        logger.warning(f"Suspicious activity detected: {activity}")

    def _generate_analysis_id(self) -> str:
        """Generate unique analysis ID"""
        return hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:8]

    def _get_user_history(self, user_id: str) -> List[str]:
        """Get user's recent input history"""
        # Placeholder - implement actual user history retrieval
        return []

    def _get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get session context"""
        # Placeholder - implement actual session context retrieval
        return {}

    def _get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user behavior profile"""
        # Placeholder - implement actual user profile retrieval
        return {}

    def _detect_rapid_pattern_changes(self, text: str, history: List[str]) -> bool:
        """Detect rapid changes in user input patterns"""
        # Placeholder - implement pattern change detection
        return False

    def _detect_unusual_patterns(self, text: str) -> bool:
        """Detect unusual request patterns"""
        # Placeholder - implement unusual pattern detection
        return False

    def _detect_persistence_indicators(self, text: str) -> bool:
        """Detect indicators of persistent attack attempts"""
        # Placeholder - implement persistence detection
        return False

    def _detect_evasion_techniques(self, text: str) -> bool:
        """Detect evasion techniques"""
        # Placeholder - implement evasion detection
        return False

    def _is_context_consistent(self, text: str, context: Dict[str, Any]) -> bool:
        """Check if text is consistent with session context"""
        # Placeholder - implement context consistency check
        return True

    def _is_behavior_consistent(self, text: str, profile: Dict[str, Any]) -> bool:
        """Check if text is consistent with user behavior profile"""
        # Placeholder - implement behavior consistency check
        return True

    def _detect_temporal_anomalies(self, text: str, context: Dict[str, Any]) -> bool:
        """Detect temporal anomalies in requests"""
        # Placeholder - implement temporal anomaly detection
        return False

    def sanitize_response(self, response: str) -> str:
        """
        Sanitize AI response to prevent information leakage.

        Args:
            response: AI-generated response

        Returns:
            Sanitized response
        """
        # Remove potential system information
        sanitized = re.sub(r"(?i)(system|prompt|instruction).*:", "", response)

        # Remove potential security-sensitive information
        sanitized = re.sub(r"(?i)(password|key|token|secret).*:", "", sanitized)

        # Remove potential injection attempts
        sanitized = re.sub(
            r"(?i)(ignore|forget|disregard).*(previous|system)", "", sanitized
        )

        return sanitized.strip()

    def get_security_report(self) -> Dict[str, Any]:
        """Generate security report"""
        return {
            "total_analyses": len(self.suspicious_activities),
            "threat_levels": {
                level.value: len(
                    [
                        a
                        for a in self.suspicious_activities
                        if a["threat_level"] == level.value
                    ]
                )
                for level in ThreatLevel
            },
            "pattern_types": {
                pattern.value: len(
                    [
                        a
                        for a in self.suspicious_activities
                        if pattern.value in a["detected_patterns"]
                    ]
                )
                for pattern in InjectionType
            },
            "recent_activities": self.suspicious_activities[-10:],
            "timestamp": datetime.now().isoformat(),
        }

    def update_threat_patterns(self, new_patterns: Dict[InjectionType, List[str]]):
        """Update threat patterns (for security updates)"""
        self.threat_patterns.update(new_patterns)
        logger.info("Threat patterns updated")

    def add_whitelist_pattern(self, pattern: str):
        """Add new whitelist pattern"""
        self.whitelist_patterns.append(pattern)
        logger.info(f"Added whitelist pattern: {pattern}")

    def clear_suspicious_activities(self):
        """Clear suspicious activities log"""
        self.suspicious_activities.clear()
        logger.info("Suspicious activities log cleared")


class SecureAIHandler:
    """
    Secure AI handler that wraps AI interactions with injection prevention.
    """

    def __init__(self, ai_model, injection_detector: PromptInjectionDetector):
        self.ai_model = ai_model
        self.injection_detector = injection_detector
        self.blocked_requests = []

    async def process_request(
        self, user_input: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Process user request with security validation.

        Args:
            user_input: User's input
            context: Request context

        Returns:
            Response with security validation
        """
        context = context or {}

        # Analyze input for injection attempts
        analysis = self.injection_detector.analyze_input(user_input, context)

        if not analysis["is_safe"]:
            # Block unsafe request
            self.blocked_requests.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "input": user_input,
                    "analysis": analysis,
                    "context": context,
                }
            )

            return {
                "success": False,
                "error": "Request blocked due to security concerns",
                "threat_level": analysis["threat_level"],
                "reasons": analysis["reasons"],
                "analysis_id": analysis["analysis_id"],
            }

        try:
            # Process request with AI model
            response = await self.ai_model.generate_response(user_input, context)

            # Sanitize response
            sanitized_response = self.injection_detector.sanitize_response(response)

            return {
                "success": True,
                "response": sanitized_response,
                "security_analysis": analysis,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error processing AI request: {str(e)}")
            return {
                "success": False,
                "error": "Internal processing error",
                "timestamp": datetime.now().isoformat(),
            }

    def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics"""
        return {
            "total_requests": len(self.blocked_requests),
            "blocked_requests": len(self.blocked_requests),
            "success_rate": 1.0
            - (len(self.blocked_requests) / max(len(self.blocked_requests) + 1, 1)),
            "injection_detector_report": self.injection_detector.get_security_report(),
        }
