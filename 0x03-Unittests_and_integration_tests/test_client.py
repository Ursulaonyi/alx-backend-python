#!/usr/bin/env python3
"""Unit tests for GithubOrgClient methods."""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Tests for the GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct value
        and get_json is called once with the correct URL."""
        mock_get_json.return_value = {"login": org_name}

        client = GithubOrgClient(org_name)
        result = client.org

        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)
        self.assertEqual(result, {"login": org_name})

    def test_public_repos_url(self):
        """Test that _public_repos_url returns expected repos_url
        from the mocked org property."""
        client = GithubOrgClient("test_org")
        mocked_org_payload = {"repos_url": "https://api.github.com/orgs/test_org/repos"}

        with patch.object(
            GithubOrgClient, "org", new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = mocked_org_payload

            result = client._public_repos_url
            self.assertEqual(result, mocked_org_payload["repos_url"])


if __name__ == "__main__":
    unittest.main()
