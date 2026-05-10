"""Tests for the Click CLI."""

import json

import pytest
from click.testing import CliRunner

from sample_sizer.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


# --------------------------------------------------------------------------- #
# calculate command — smoke tests for all methods
# --------------------------------------------------------------------------- #


class TestCalculateSmokeTests:
    @pytest.mark.parametrize(
        "method",
        [
            "interviews",
            "focus_groups",
            "diary_study",
            "usability_test",
            "card_sorting",
            "tree_testing",
            "survey",
            "ab_test",
            "experiment",
            "correlation",
        ],
    )
    def test_rich_output_succeeds(self, runner, method):
        result = runner.invoke(cli, ["calculate", method])
        assert result.exit_code == 0, result.output

    @pytest.mark.parametrize(
        "method",
        [
            "interviews",
            "focus_groups",
            "diary_study",
            "usability_test",
            "card_sorting",
            "tree_testing",
            "survey",
            "ab_test",
            "experiment",
            "correlation",
        ],
    )
    def test_json_output_is_valid(self, runner, method):
        result = runner.invoke(cli, ["calculate", method, "--json-output"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert "recommended_n" in data
        assert "method" in data
        assert data["recommended_n"] > 0


# --------------------------------------------------------------------------- #
# JSON structure
# --------------------------------------------------------------------------- #


class TestJsonOutputStructure:
    def test_all_required_keys_present(self, runner):
        result = runner.invoke(cli, ["calculate", "survey", "--json-output"])
        data = json.loads(result.output)
        required_keys = [
            "method",
            "method_type",
            "recommended_n",
            "min_n",
            "max_n",
            "rationale",
            "power_notes",
            "caveats",
            "narrative",
        ]
        for key in required_keys:
            assert key in data, f"Missing key: {key}"

    def test_narrative_null_without_llm(self, runner):
        result = runner.invoke(cli, ["calculate", "interviews", "--json-output"])
        data = json.loads(result.output)
        assert data["narrative"] is None

    def test_min_le_recommended_le_max(self, runner):
        result = runner.invoke(cli, ["calculate", "survey", "--json-output"])
        data = json.loads(result.output)
        assert data["min_n"] <= data["recommended_n"] <= data["max_n"]

    def test_method_type_value(self, runner):
        result = runner.invoke(cli, ["calculate", "interviews", "--json-output"])
        data = json.loads(result.output)
        assert data["method_type"] == "qualitative"

        result = runner.invoke(cli, ["calculate", "survey", "--json-output"])
        data = json.loads(result.output)
        assert data["method_type"] == "quantitative"


# --------------------------------------------------------------------------- #
# Parameter passing
# --------------------------------------------------------------------------- #


class TestParameterPassing:
    def test_homogeneity_homogeneous(self, runner):
        result = runner.invoke(
            cli, ["calculate", "interviews", "--homogeneity", "homogeneous", "--json-output"]
        )
        data = json.loads(result.output)
        assert data["recommended_n"] == 12

    def test_homogeneity_heterogeneous(self, runner):
        result = runner.invoke(
            cli, ["calculate", "interviews", "--homogeneity", "heterogeneous", "--json-output"]
        )
        data = json.loads(result.output)
        assert data["recommended_n"] == 25

    def test_effect_size_small(self, runner):
        result_small = runner.invoke(
            cli, ["calculate", "ab_test", "--effect-size", "small", "--json-output"]
        )
        result_large = runner.invoke(
            cli, ["calculate", "ab_test", "--effect-size", "large", "--json-output"]
        )
        data_small = json.loads(result_small.output)
        data_large = json.loads(result_large.output)
        assert data_small["recommended_n"] > data_large["recommended_n"]

    def test_population_size(self, runner):
        result_inf = runner.invoke(cli, ["calculate", "survey", "--json-output"])
        result_fin = runner.invoke(
            cli, ["calculate", "survey", "--population", "500", "--json-output"]
        )
        n_inf = json.loads(result_inf.output)["recommended_n"]
        n_fin = json.loads(result_fin.output)["recommended_n"]
        assert n_fin < n_inf

    def test_usability_goal_benchmark(self, runner):
        result = runner.invoke(
            cli,
            ["calculate", "usability_test", "--usability-goal", "benchmark", "--json-output"],
        )
        data = json.loads(result.output)
        assert data["recommended_n"] == 35

    def test_confidence_99(self, runner):
        result_95 = runner.invoke(cli, ["calculate", "survey", "--confidence", "0.95", "--json-output"])
        result_99 = runner.invoke(cli, ["calculate", "survey", "--confidence", "0.99", "--json-output"])
        n_95 = json.loads(result_95.output)["recommended_n"]
        n_99 = json.loads(result_99.output)["recommended_n"]
        assert n_99 > n_95


# --------------------------------------------------------------------------- #
# Error handling
# --------------------------------------------------------------------------- #


class TestErrorHandling:
    def test_invalid_method(self, runner):
        result = runner.invoke(cli, ["calculate", "nonexistent_method"])
        assert result.exit_code != 0

    def test_help_flag(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "sample-sizer" in result.output

    def test_calculate_help(self, runner):
        result = runner.invoke(cli, ["calculate", "--help"])
        assert result.exit_code == 0
        assert "METHOD" in result.output


# --------------------------------------------------------------------------- #
# batch command
# --------------------------------------------------------------------------- #


class TestBatchCommand:
    def test_batch_from_json_file(self, runner, tmp_path):
        batch_data = [
            {"method": "interviews"},
            {"method": "survey", "confidence_level": 0.95, "margin_of_error": 0.05},
            {"method": "ab_test", "effect_size": "medium", "power": 0.80},
        ]
        f = tmp_path / "batch.json"
        f.write_text(json.dumps(batch_data))

        result = runner.invoke(cli, ["batch", str(f)])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 3
        for item in data:
            assert "recommended_n" in item
            assert item["recommended_n"] > 0

    def test_batch_output_to_file(self, runner, tmp_path):
        batch_data = [{"method": "experiment"}]
        input_f = tmp_path / "batch.json"
        output_f = tmp_path / "out.json"
        input_f.write_text(json.dumps(batch_data))

        result = runner.invoke(cli, ["batch", str(input_f), "--output", str(output_f)])
        assert result.exit_code == 0
        assert output_f.exists()
        data = json.loads(output_f.read_text())
        assert len(data) == 1

    def test_batch_handles_invalid_method_gracefully(self, runner, tmp_path):
        batch_data = [{"method": "invalid_method"}, {"method": "interviews"}]
        f = tmp_path / "batch.json"
        f.write_text(json.dumps(batch_data))

        result = runner.invoke(cli, ["batch", str(f)])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 2
        assert "error" in data[0]
        assert data[1]["recommended_n"] > 0
