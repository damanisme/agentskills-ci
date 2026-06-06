from agentskills_ci.badge import badge_color, build_endpoint, build_markdown, build_url


def test_badge_color_thresholds():
    assert badge_color(100) == "brightgreen"
    assert badge_color(90) == "brightgreen"
    assert badge_color(80) == "green"
    assert badge_color(65) == "yellow"
    assert badge_color(45) == "orange"
    assert badge_color(10) == "red"


def test_build_endpoint_is_shields_schema():
    endpoint = build_endpoint(100, label="skill score")
    assert endpoint == {
        "schemaVersion": 1,
        "label": "skill score",
        "message": "100",
        "color": "brightgreen",
    }


def test_build_url_encodes_label_and_score():
    url = build_url(72, label="skill score")
    assert url == "https://img.shields.io/badge/skill%20score-72-yellow"


def test_build_markdown_links_back_when_repo_given():
    md = build_markdown(100, label="skill score", repo="https://github.com/me/repo")
    assert md == (
        "[![skill score](https://img.shields.io/badge/skill%20score-100-brightgreen)]"
        "(https://github.com/me/repo)"
    )


def test_build_markdown_without_repo_is_image_only():
    md = build_markdown(100, label="skill score")
    assert md == "![skill score](https://img.shields.io/badge/skill%20score-100-brightgreen)"
