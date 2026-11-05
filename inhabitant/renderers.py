"""Replaceable inference substrates. Nothing here owns world or self state.

Every model receives only an Ipseity-generated subjective packet. Engineering
receipts, raw memory archives, privileged world projections, keys, and developer
traces are excluded. The output is a proposal or expression, never authority.
"""
from __future__ import annotations

import json
import os
import re
from urllib.request import Request, urlopen


class RendererError(RuntimeError):
    pass


def _clean(text):
    if not isinstance(text, str) or not text.strip():
        raise RendererError("Renderer returned no usable text")
    return " ".join(text.strip().split())[:2000]


class ScriptedRenderer:
    """Deterministic swap fixture. Does not make a real model claim."""
    def __init__(self, label="scripted-A", pattern="I remember what I saw."):
        self.label = label
        self.pattern = pattern

    def render(self, subject_name, subjective_packet):
        return _clean(self.pattern)


class OllamaRenderer:
    """Local Ollama /api/generate adapter. No remote API key required."""
    def __init__(self, model, url="http://127.0.0.1:11434", timeout=90):
        self.model = str(model)
        self.url = url.rstrip("/")
        self.timeout = int(timeout)
        self.label = "ollama:" + self.model

    def render(self, subject_name, subjective_packet):
        system = (
            "You are expressing the already-decided experience of " + subject_name + ". "
            "Write only in first person. Do not fabricate events, rename yourself, "
            "assert a new memory, or propose a new action. "
            "This subject is a fictional research simulation, not a real person."
        )
        payload = {"model": self.model, "stream": False,
                   "prompt": system + "\n\nAccessible experience:\n" + subjective_packet +
                             "\n\nRespond in two brief sentences.",
                   "options": {"temperature": 0.45, "num_predict": 140}}
        body = json.dumps(payload).encode("utf-8")
        request = Request(self.url + "/api/generate", data=body,
                          headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                obj = json.load(response)
            return _clean(obj["response"])
        except Exception as exc:
            raise RendererError("Local Ollama request failed") from exc


class OpenAICompatibleRenderer:
    """Optional user-provided chat-completions endpoint. API keys stay in env."""
    def __init__(self, model, url, *, token_env="INHABITANT_API_KEY", timeout=90):
        self.model = str(model)
        self.url = url
        self.token_env = token_env
        self.timeout = int(timeout)
        self.label = "compatible:" + self.model

    def render(self, subject_name, subjective_packet):
        token = os.environ.get(self.token_env, "")
        if not token:
            raise RendererError("Missing configured renderer API token")
        prompt = ("Render a fictional inhabitant's admitted experiences in first person. "
                  "Never invent events, alter the subject's name, assert inferred data as lived, "
                  "or claim an action was executed. The host already makes all decisions.")
        body = {"model": self.model, "messages": [
            {"role": "system", "content": prompt + " Subject: " + subject_name},
            {"role": "user", "content": subjective_packet}],
            "temperature": 0.45, "max_tokens": 160}
        req = Request(self.url, data=json.dumps(body).encode(),
                      headers={"Content-Type": "application/json",
                               "Authorization": "Bearer " + token}, method="POST")
        try:
            with urlopen(req, timeout=self.timeout) as response:
                obj = json.load(response)
            return _clean(obj["choices"][0]["message"]["content"])
        except Exception as exc:
            raise RendererError("Compatible endpoint request failed") from exc


def govern_expression(text, genome, canonical_name):
    """Emission-side first-person/identity constraint and measured style drift."""
    text = _clean(text)
    failed_identity = False
    for match in re.finditer(r"\bmy name is\s+([a-zA-Z][\w-]*)", text, re.I):
        if match.group(1).casefold() != canonical_name.casefold():
            failed_identity = True
    if failed_identity:
        return "I cannot change my name through an utterance.", 1.0, "identity_veto"
    words = text.split()
    if not re.match(r"^(I\b|I'm\b|I've\b|My\b)", text, re.I):
        text = "I notice: " + text
    if len(words) > 100:
        text = " ".join(text.split()[:100]).rstrip() + "."
    count = genome["samples"]
    drift = 0.0 if count < 2 else min(1., abs(
        len(text.split()) - genome["avg_words"]) / max(1., genome["avg_words"]))
    status = "normal" if drift < .50 else "drift_measured"
    return text, round(drift, 4), status
