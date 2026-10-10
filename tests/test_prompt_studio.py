import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from research_agent.web.app import app
from research_agent.studio.prompt_manager import PromptManager
from research_agent.studio.chain_manager import ChainManager, PipelineConfig
from research_agent.llm.mock_provider import MockProvider

client = TestClient(app)

def test_prompt_manager_list():
    prompts = PromptManager.list_prompts()
    assert len(prompts) >= 15
    filenames = [p.filename for p in prompts]
    assert "stock_critic_disconfirmation.md" in filenames
    assert "topic_agent.md" in filenames
    assert "interview_intel.md" in filenames

def test_prompt_manager_get_and_extract_variables():
    prompt = PromptManager.get_prompt("stock_entity_resolution.md")
    assert prompt.filename == "stock_entity_resolution.md"
    assert "user_query" in prompt.variables
    assert "market_data" in prompt.variables
    assert len(prompt.content) > 0

def test_prompt_manager_update_and_reset():
    filename = "stock_macro_sector.md"
    original = PromptManager.get_prompt(filename).content
    
    # Update prompt
    updated = PromptManager.update_prompt(filename, original + "\n\n<!-- Studio Custom Test Instruction -->")
    assert "<!-- Studio Custom Test Instruction -->" in updated.content
    assert updated.is_modified is True
    
    # Reset prompt
    reset = PromptManager.reset_prompt(filename)
    assert "<!-- Studio Custom Test Instruction -->" not in reset.content
    assert reset.is_modified is False

def test_prompt_manager_test_prompt():
    with patch("research_agent.studio.prompt_manager.get_llm_provider", return_value=MockProvider()):
        result = PromptManager.test_prompt(
            filename="stock_entity_resolution.md",
            variables={"user_query": "NVDA", "market_data": "{'ticker': 'NVDA'}"}
        )
        assert result["success"] is True
        assert "NVDA" in result["formatted_prompt"]
        assert result["response"] is not None

def test_api_list_prompts():
    res = client.get("/api/prompts")
    assert res.status_code == 200
    data = res.json()
    assert "prompts" in data
    assert len(data["prompts"]) >= 15

def test_api_get_and_update_prompt():
    filename = "stock_valuation_analysis.md"
    res = client.get(f"/api/prompts/{filename}")
    assert res.status_code == 200
    data = res.json()
    original_content = data["content"]
    
    # Update via PUT
    res_put = client.put(f"/api/prompts/{filename}", json={"content": original_content + "\n<!-- test tag -->"})
    assert res_put.status_code == 200
    assert "<!-- test tag -->" in res_put.json()["content"]
    
    # Reset via POST
    res_reset = client.post(f"/api/prompts/{filename}/reset")
    assert res_reset.status_code == 200
    assert "<!-- test tag -->" not in res_reset.json()["content"]

def test_api_pipeline_config():
    res = client.get("/api/pipeline/config")
    assert res.status_code == 200
    cfg = res.json()
    assert "llm_provider" in cfg
    assert "enable_critic_agent" in cfg
    
    # Update config
    cfg["enable_critic_agent"] = False
    res_put = client.put("/api/pipeline/config", json=cfg)
    assert res_put.status_code == 200
    assert res_put.json()["enable_critic_agent"] is False
    
    # Reset config back
    cfg["enable_critic_agent"] = True
    client.put("/api/pipeline/config", json=cfg)

def test_api_pipeline_graph():
    res = client.get("/api/pipeline/graph")
    assert res.status_code == 200
    data = res.json()
    assert "domains" in data
    assert len(data["domains"]) == 3
