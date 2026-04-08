from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path

from src.config import load_config, validate_config
from src.digest_builder import build_digest
from src.emailer import render_html_digest, render_text_digest, send_digest_email
from src.history import load_recommendation_history, save_recommendation_history


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and email a daily Zotero paper digest.")
    parser.add_argument("--config", default="config.yaml", help="Path to config YAML")
    parser.add_argument("--output-dir", default="outputs", help="Directory for generated artifacts")
    parser.add_argument(
        "--history-file",
        default=".state/recommended_history.json",
        help="Path to persistent recommendation history JSON",
    )
    parser.add_argument("--skip-email", action="store_true", help="Generate artifacts but do not send email")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    configure_logging(output_dir / "run.log")

    config = load_config(args.config)
    validate_config(config, require_email=not args.skip_email)
    history_keys = load_recommendation_history(args.history_file)
    logging.info("Loaded %s recommendation history identity keys.", len(history_keys))
    digest = build_digest(config, os.environ["ZOTERO_API_KEY"], recommendation_history=history_keys)

    if config.output.save_json:
        (output_dir / "digest.json").write_text(
            json.dumps(digest.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    if config.output.save_html:
        (output_dir / "digest.html").write_text(render_html_digest(digest), encoding="utf-8")
    (output_dir / "digest.txt").write_text(render_text_digest(digest), encoding="utf-8")

    if args.skip_email:
        logging.info("Skipping email because --skip-email was provided.")
    else:
        send_digest_email(config.email, digest)
        save_recommendation_history(args.history_file, digest, history_keys)
        logging.info("Digest email sent to %s", config.email.to_email)
        logging.info("Updated recommendation history at %s", args.history_file)
    return 0


def configure_logging(log_path: Path) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(log_path, encoding="utf-8")],
    )


if __name__ == "__main__":
    raise SystemExit(main())
