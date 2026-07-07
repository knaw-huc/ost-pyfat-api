import os
import yaml
import tempfile
import requests

from typing import List, Dict
import src.resources as resources


class MetricsProcessor:
    # Class attributes
    _instance = None

    def __new__(cls, metrics_file):
        """Implement the singleton pattern"""
        if cls._instance is None:
            cls._instance = super(MetricsProcessor, cls).__new__(cls)
            cls._initialize(metrics_file)
        # else:
        #     print('Preprocessor already exists')
        return cls._instance

    @classmethod
    def _initialize(cls, metrics_file: str):
        """Initialize the singleton instance"""
        cls._metrics_file_location = metrics_file
        cls._metrics_version = None
        cls._metrics_infra = None
        cls._metrics_list = []
        cls._metrics_loc = None
        cls._metrics_total = 0
        cls._metrics_ns = None
        cls._metrics_created_by = None
        cls._metrics_tests_id_map = {}

    @classmethod
    def parse_metrics_yaml(cls):
        # Check if METRICS_FILE is a URL
        if cls._metrics_file_location.startswith(("http://", "https://")):
            response = requests.get(cls._metrics_file_location)
            response.raise_for_status()  # Raise an error for bad responses
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(response.content)
                cls._metrics_loc = temp_file.name
        else:
            cls._metrics_loc = os.path.join(os.path.dirname(resources.__file__), "metrics", cls._metrics_file_location)

        with open(str(cls._metrics_loc), 'r') as file:
            metrics_specs = yaml.load(file, Loader=yaml.FullLoader)
            cls._metrics_list = metrics_specs['metrics']
            cls._metrics_version = metrics_specs['config']['metric_version']
            if 'metric_infrastructure' in metrics_specs['config']:
                cls._metrics_infra = metrics_specs['config']['metric_infrastructure']
            cls._metrics_created_by = metrics_specs['created_by']
            cls._metrics_ns = metrics_specs['config']['metric_namespaces']
        for metric in cls._metrics_list:
            # Extract all metric_test_identifier values from metric_tests
            test_ids = [test['metric_test_identifier'] for test in metric.get('metric_tests', [])]
            cls._metrics_tests_id_map[metric['metric_identifier']] = test_ids

    @classmethod
    def get_total_metrics(cls) -> int:
        """Get the total number of metrics"""
        return len(cls._metrics_list)

    @classmethod
    def get_metrics_tests_id_map(cls) -> dict[str, list]:
        """Gets the metrics tests id map: key: metric_identifier, value: list of metric_test_identifier"""
        return cls._metrics_tests_id_map

    @classmethod
    def get_all_metric_ids(cls) -> list[str]:
        """Gets the list of all metric identifiers"""
        return [metric['metric_identifier'] for metric in cls._metrics_list]

    @classmethod
    def all_test_ids(cls) -> list:
        """Get a flat list of all test IDs from all metrics."""
        return [test_id for test_ids in cls._metrics_tests_id_map.values() for test_id in test_ids]

    @classmethod
    def is_valid_testid(cls, test_id) -> bool:
        """Check if a given test_id exists in any metric's test list."""
        for test_ids in cls._metrics_tests_id_map.values():
            if test_id in test_ids:
                return True
        return False

    @classmethod
    def get_metrics_created_by(cls) -> str:
        """Get the creator of the metrics"""
        return cls._metrics_created_by

    @classmethod
    def get_metrics_version(cls) -> str:
        """Get the version of the metrics"""
        return str(cls._metrics_version)

    @classmethod
    def get_metrics(cls) -> List[dict]:
        """Get the list of metrics"""
        return cls._metrics_list

    @classmethod
    def get_nspace_map(cls) -> Dict[str, str]:
        """Get the namespace map of the metrics"""
        return cls._metrics_ns

    @classmethod
    def get_metrictest_by_testid(cls, metric_test_identifier: str) -> dict | None:
        """Return the metric_test object (dict) for a given metric_test_identifier, or None if not found."""
        for metric in cls._metrics_list:
            for test in metric.get('metric_tests', []):
                if test.get('metric_test_identifier') == metric_test_identifier:
                    return test
        return None

    @classmethod
    def get_metric_by_testid(cls, metric_test_identifier: str) -> dict | None:
        """Return the parent metric object (dict) for a given metric_test_identifier, or None if not found."""
        for metric in cls._metrics_list:
            for test in metric.get('metric_tests', []):
                if test.get('metric_test_identifier') == metric_test_identifier:
                    return metric
        return None

    @classmethod
    def get_infrastructure(cls) -> str | None:
        return cls._metrics_infra

    @classmethod
    def get_metric_guidance_by_metricid(cls, metric_id: str) -> str | None:
        """Return the guidance text for a given metric identifier."""
        for metric in cls._metrics_list:
            if metric.get('metric_identifier') != metric_id:
                continue

            guidance = metric.get('metric_guidance')
            if guidance is None:
                return None

            if isinstance(guidance, str):
                return guidance

            if isinstance(guidance, dict):
                for key in ('en', 'eng', 'english', 'default', 'text', 'value'):
                    value = guidance.get(key)
                    if isinstance(value, str) and value.strip():
                        return value
                return None

            if isinstance(guidance, list):
                parts = [item for item in guidance if isinstance(item, str) and item.strip()]
                return '\n'.join(parts) if parts else None

            return str(guidance)

        return None

    @classmethod
    def get_all_metric_guidance(cls) -> Dict[str, str]:
        """Gets all metric guidance texts as value by metric_identifier as dict key."""
        guidance_map = {}
        for metric in cls._metrics_list:
            metric_id = metric.get('metric_identifier')
            guidance_text = metric.get('metric_guidance')
            if guidance_text is not None:
                guidance_map[metric_id] = guidance_text
        return guidance_map

    @classmethod
    def get_all_test_guidance(cls) -> Dict[str, str]:
        """Gets all test guidance texts as value by metric_test_identifier as dict key."""
        tset_guidance_map = {}
        for metric in cls._metrics_list:
            for test in metric.get('metric_tests', []):
                test_id = test.get('metric_test_identifier')
                guidance_text = test.get('metric_test_guidance')
                if guidance_text is not None:
                    tset_guidance_map[test_id] = guidance_text
        return tset_guidance_map

    @classmethod
    def get_metric_by_metricid(cls, metric_id: str) -> dict | None:
        """Return the Metric object for a given metric identifier."""
        for metric in cls._metrics_list:
            if metric.get('metric_identifier') != metric_id:
                continue
            return metric
        return None