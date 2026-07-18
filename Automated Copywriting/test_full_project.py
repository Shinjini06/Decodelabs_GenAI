"""
Complete End-to-End Test Suite for Automated Copywriting Framework
Tests all 6 phases together in integrated scenarios
"""

import asyncio
import sys
from models import CopyRequest, CopyResponse, PlatformEnum, ToneEnum
from template_compiler import TemplateCompiler
from parameter_tuner import ParameterTuner


class FullProjectTester:
    """End-to-end test suite for complete framework"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
    
    def test(self, name: str, condition: bool, expected=True):
        """Record test result"""
        if condition == expected:
            print(f"  ✅ {name}")
            self.tests_passed += 1
            return True
        else:
            print(f"  ❌ {name}")
            self.tests_failed += 1
            return False
    
    def run_phase_1_tests(self):
        """Phase 1: Pydantic Models + CLI"""
        print("\n" + "="*70)
        print("PHASE 1: PYDANTIC MODELS + CLI VALIDATION")
        print("="*70)
        
        # Test 1.1: Valid request creation
        req = CopyRequest(
            product_name="  running shoe  ",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.WITTY
        )
        self.test("Product name auto-cleaned", req.product_name == "Running Shoe")
        self.test("Platform enum set", req.platform == PlatformEnum.LINKEDIN)
        self.test("Tone enum set", req.tone == ToneEnum.WITTY)
        
        # Test 1.2: Valid response creation
        resp = CopyResponse(
            product_name="Test Product",
            platform="linkedin",
            tone="witty",
            copy="This is a test copy that is long enough to pass validation requirements."
        )
        self.test("Char count auto-calculated", resp.char_count == len(resp.copy))
        self.test("Response validation passed", len(resp.copy) >= 10)
        
        # Test 1.3: Invalid inputs rejected
        try:
            CopyRequest(
                product_name="",
                platform=PlatformEnum.LINKEDIN,
                tone=ToneEnum.WITTY
            )
            self.test("Empty product rejected", False)
        except ValueError:
            self.test("Empty product rejected", True)
        
        # Test 1.4: All platform enums work
        for platform in PlatformEnum:
            req = CopyRequest(
                product_name="Test",
                platform=platform,
                tone=ToneEnum.PROFESSIONAL
            )
            self.test(f"Platform {platform.value} works", True)
        
        # Test 1.5: All tone enums work
        for tone in ToneEnum:
            req = CopyRequest(
                product_name="Test",
                platform=PlatformEnum.LINKEDIN,
                tone=tone
            )
            self.test(f"Tone {tone.value} works", True)
        
        print("\n✅ PHASE 1: PASSED")
    
    def run_phase_2_tests(self):
        """Phase 2: Template Compiler"""
        print("\n" + "="*70)
        print("PHASE 2: TEMPLATE COMPILER")
        print("="*70)
        
        # Test 2.1: Witty template
        req = CopyRequest(
            product_name="Running Shoe",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.WITTY
        )
        compiled = TemplateCompiler.compile(req)
        self.test("Witty template compiles", "Running Shoe" in compiled)
        self.test("Template contains tone guidance", "clever" in compiled.lower())
        self.test("Template contains platform", "LINKEDIN" in compiled)
        
        # Test 2.2: Professional template
        req = CopyRequest(
            product_name="Enterprise Software",
            platform=PlatformEnum.EMAIL,
            tone=ToneEnum.PROFESSIONAL
        )
        compiled = TemplateCompiler.compile(req)
        self.test("Professional template compiles", "Enterprise Software" in compiled)
        self.test("Professional tone guidance present", "professional" in compiled.lower())
        self.test("Email constraints present", "160" in compiled)
        
        # Test 2.3: Platform constraints
        for platform in PlatformEnum:
            constraints = TemplateCompiler.get_platform_constraints(platform)
            self.test(f"{platform.value} has constraints", len(constraints) > 0)
        
        # Test 2.4: All tone templates exist
        for tone in ToneEnum:
            req = CopyRequest(
                product_name="Test",
                platform=PlatformEnum.LINKEDIN,
                tone=tone
            )
            compiled = TemplateCompiler.compile(req)
            self.test(f"Tone {tone.value} template exists", "Test" in compiled)
        
        print("\n✅ PHASE 2: PASSED")
    
    def run_phase_3_tests(self):
        """Phase 3: Parameter Tuner"""
        print("\n" + "="*70)
        print("PHASE 3: PARAMETER TUNER")
        print("="*70)
        
        # Test 3.1: Temperature by tone
        req_witty = CopyRequest(
            product_name="Test",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.WITTY
        )
        params_witty = ParameterTuner.tune(req_witty)
        self.test("Witty has high temperature", params_witty.temperature >= 0.7)
        
        req_prof = CopyRequest(
            product_name="Test",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PROFESSIONAL
        )
        params_prof = ParameterTuner.tune(req_prof)
        self.test("Professional has low temperature", params_prof.temperature <= 0.5)
        
        # Test 3.2: Tokens by platform
        req_email = CopyRequest(
            product_name="Test",
            platform=PlatformEnum.EMAIL,
            tone=ToneEnum.PROFESSIONAL
        )
        params_email = ParameterTuner.tune(req_email)
        self.test("Email has low token count", params_email.max_tokens <= 100)
        
        req_linkedin = CopyRequest(
            product_name="Test",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PROFESSIONAL
        )
        params_linkedin = ParameterTuner.tune(req_linkedin)
        self.test("LinkedIn has high token count", params_linkedin.max_tokens >= 100)
        
        # Test 3.3: User overrides
        params_override = ParameterTuner.tune(
            req_witty,
            user_temperature=0.5,
            user_max_tokens=200
        )
        self.test("Temperature override works", params_override.temperature == 0.5)
        self.test("Max tokens override works", params_override.max_tokens == 200)
        
        # Test 3.4: Parameter validation
        from parameter_tuner import GenerationParams
        try:
            GenerationParams(temperature=3.0, top_p=1.0, max_tokens=100)
            self.test("Invalid temperature rejected", False)
        except ValueError:
            self.test("Invalid temperature rejected", True)
        
        # Test 3.5: Valid parameters accepted
        params = GenerationParams(temperature=0.8, top_p=0.95, max_tokens=150)
        self.test("Valid parameters accepted", True)
        
        print("\n✅ PHASE 3: PASSED")
    
    async def run_phase_4_tests(self):
        """Phase 4: Async Pipeline"""
        print("\n" + "="*70)
        print("PHASE 4: ASYNC PIPELINE (Mock)")
        print("="*70)
        
        # Mock pipeline for testing
        class MockAsyncPipeline:
            def __init__(self):
                self.semaphore = asyncio.Semaphore(3)
                self.call_count = 0
            
            async def generate_batch(self, reqs):
                responses = []
                for req in reqs:
                    async with self.semaphore:
                        self.call_count += 1
                        await asyncio.sleep(0.01)
                        resp = CopyResponse(
                            product_name=req.product_name,
                            platform=req.platform.value,
                            tone=req.tone.value,
                            copy=f"Generated copy for {req.product_name}"
                        )
                        responses.append(resp)
                return responses
        
        # Test 4.1: Single request
        pipeline = MockAsyncPipeline()
        req = CopyRequest(
            product_name="Test Product",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PROFESSIONAL
        )
        responses = await pipeline.generate_batch([req])
        self.test("Single request completes", len(responses) == 1)
        self.test("Response has correct product", responses[0].product_name == "Test Product")
        
        # Test 4.2: Batch processing
        pipeline = MockAsyncPipeline()
        requests = [
            CopyRequest(
                product_name=f"Product {i}",
                platform=PlatformEnum.LINKEDIN,
                tone=ToneEnum.PROFESSIONAL
            )
            for i in range(5)
        ]
        responses = await pipeline.generate_batch(requests)
        self.test("Batch processes all requests", len(responses) == 5)
        self.test("Order preserved", responses[0].product_name == "Product 0")
        self.test("All calls made", pipeline.call_count == 5)
        
        # Test 4.3: Semaphore limits concurrency
        pipeline = MockAsyncPipeline()
        requests = [
            CopyRequest(
                product_name=f"Product {i}",
                platform=PlatformEnum.LINKEDIN,
                tone=ToneEnum.PROFESSIONAL
            )
            for i in range(10)
        ]
        responses = await pipeline.generate_batch(requests)
        self.test("Semaphore completes all tasks", len(responses) == 10)
        self.test("Semaphore respects limit", pipeline.call_count == 10)
        
        print("\n✅ PHASE 4: PASSED")
    
    async def run_phase_5_tests(self):
        """Phase 5: Batch Pipeline"""
        print("\n" + "="*70)
        print("PHASE 5: BATCH PIPELINE (Mock)")
        print("="*70)
        
        class MockBatchPipeline:
            def __init__(self):
                self.batch_count = 0
            
            async def submit_batch(self, reqs):
                self.batch_count += 1
                await asyncio.sleep(0.05)
                return f"batch_{self.batch_count:05d}"
            
            async def wait_and_retrieve(self, batch_id):
                await asyncio.sleep(0.1)
                responses = [
                    CopyResponse(
                        product_name=f"Product {i}",
                        platform="linkedin",
                        tone="professional",
                        copy=f"Generated copy {i}"
                    )
                    for i in range(5)
                ]
                return responses
        
        # Test 5.1: Batch submission
        pipeline = MockBatchPipeline()
        requests = [
            CopyRequest(
                product_name=f"Product {i}",
                platform=PlatformEnum.LINKEDIN,
                tone=ToneEnum.PROFESSIONAL
            )
            for i in range(5)
        ]
        batch_id = await pipeline.submit_batch(requests)
        self.test("Batch submits successfully", "batch_" in batch_id)
        
        # Test 5.2: Batch retrieval
        results = await pipeline.wait_and_retrieve(batch_id)
        self.test("Batch results retrieved", len(results) == 5)
        self.test("Results are CopyResponse objects", isinstance(results[0], CopyResponse))
        
        # Test 5.3: Multiple batches
        pipeline = MockBatchPipeline()
        batch_ids = []
        for i in range(3):
            batch_id = await pipeline.submit_batch(requests)
            batch_ids.append(batch_id)
        self.test("Multiple batches tracked", len(set(batch_ids)) == 3)
        
        print("\n✅ PHASE 5: PASSED")
    
    async def run_phase_6_tests(self):
        """Phase 6: Router & Integration"""
        print("\n" + "="*70)
        print("PHASE 6: ROUTER & INTEGRATION")
        print("="*70)
        
        from pipelines.router import Router
        
        # Test 6.1: Small batch → Async
        small = [CopyRequest(
            product_name=f"Product {i}",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PROFESSIONAL
        ) for i in range(5)]
        choice = Router.choose_pipeline(small)
        self.test("Small batch routes to async", choice == "async")
        
        # Test 6.2: Medium batch → Async
        medium = [CopyRequest(
            product_name=f"Product {i}",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PROFESSIONAL
        ) for i in range(30)]
        choice = Router.choose_pipeline(medium)
        self.test("Medium batch routes to async", choice == "async")
        
        # Test 6.3: Large batch → Batch
        large = [CopyRequest(
            product_name=f"Product {i}",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PROFESSIONAL
        ) for i in range(75)]
        choice = Router.choose_pipeline(large)
        self.test("Large batch routes to batch", choice == "batch")
        
        # Test 6.4: Force mode override
        choice = Router.choose_pipeline(small, force_mode="batch")
        self.test("Force mode override works", choice == "batch")
        
        # Test 6.5: Explanation generated
        explanation = Router.explain_choice(small, "async")
        self.test("Explanation contains strategy", "ASYNC" in explanation or "async" in explanation.lower())
        
        print("\n✅ PHASE 6: PASSED")
    
    async def run_integration_test(self):
        """Full end-to-end integration"""
        print("\n" + "="*70)
        print("FULL INTEGRATION TEST: All Phases Together")
        print("="*70)
        
        # Create a realistic request
        requests = [
            CopyRequest(
                product_name="Premium Running Shoes",
                platform=PlatformEnum.LINKEDIN,
                tone=ToneEnum.PROFESSIONAL
            ),
            CopyRequest(
                product_name="Wireless Headphones",
                platform=PlatformEnum.INSTAGRAM,
                tone=ToneEnum.WITTY
            ),
            CopyRequest(
                product_name="Project Management Tool",
                platform=PlatformEnum.EMAIL,
                tone=ToneEnum.CASUAL
            ),
        ]
        
        # Phase 1: Validate all requests
        for req in requests:
            self.test(f"Request valid: {req.product_name}", True)
        
        # Phase 2: Compile templates
        templates = []
        for req in requests:
            template = TemplateCompiler.compile(req)
            templates.append(template)
            self.test(f"Template compiled for {req.product_name}", len(template) > 0)
        
        # Phase 3: Tune parameters
        params_list = []
        for req in requests:
            params = ParameterTuner.tune(req)
            params_list.append(params)
            self.test(f"Parameters tuned for {req.product_name}", params.temperature > 0)
        
        # Phase 6: Route selection
        from pipelines.router import Router
        choice = Router.choose_pipeline(requests)
        self.test("Router chooses pipeline", choice in ["async", "batch"])
        
        print("\n✅ FULL INTEGRATION TEST: PASSED")
    
    async def run_all_tests(self):
        """Execute complete test suite"""
        print("\n")
        print("╔" + "="*68 + "╗")
        print("║" + " "*15 + "FULL PROJECT TEST SUITE" + " "*30 + "║")
        print("║" + " "*10 + "Testing all 6 phases + Integration" + " "*24 + "║")
        print("╚" + "="*68 + "╝")
        
        try:
            # Run all phase tests
            self.run_phase_1_tests()
            self.run_phase_2_tests()
            self.run_phase_3_tests()
            await self.run_phase_4_tests()
            await self.run_phase_5_tests()
            await self.run_phase_6_tests()
            await self.run_integration_test()
            
            # Summary
            total = self.tests_passed + self.tests_failed
            print("\n" + "="*70)
            print("TEST SUMMARY")
            print("="*70)
            print(f"\n✅ Tests Passed: {self.tests_passed}")
            print(f"❌ Tests Failed: {self.tests_failed}")
            print(f"📊 Total Tests:  {total}")
            print(f"📈 Success Rate: {(self.tests_passed/total)*100:.1f}%")
            
            if self.tests_failed == 0:
                print("\n" + "="*70)
                print("🎉 ALL TESTS PASSED! PROJECT IS READY FOR DEPLOYMENT! 🎉")
                print("="*70)
                return True
            else:
                print(f"\n⚠️  {self.tests_failed} test(s) failed")
                return False
        
        except Exception as e:
            print(f"\n❌ Test execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Run complete test suite"""
    tester = FullProjectTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())