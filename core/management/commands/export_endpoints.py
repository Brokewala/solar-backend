import inspect
import json
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import URLPattern, URLResolver, get_resolver


class Command(BaseCommand):
    help = "Export all project endpoints to Markdown and OpenAPI JSON"

    def add_arguments(self, parser):
        parser.add_argument(
            "--format",
            default="md,json",
            help="Comma separated output formats: md,json",
        )
        parser.add_argument(
            "--out", default="ENDPOINTS.md", help="Markdown output path"
        )
        parser.add_argument(
            "--openapi", default="openapi.json", help="OpenAPI JSON path"
        )
        parser.add_argument(
            "--base-url",
            default="http://localhost:8000",
            help="Base URL for examples",
        )

    def handle(self, *args, **options):
        formats = [f.strip() for f in options["format"].split(",") if f.strip()]
        md_path = options["out"]
        json_path = options["openapi"]
        base_url = options["base_url"].rstrip("/")

        endpoints = list(self._gather_endpoints())

        if "md" in formats:
            markdown = self._render_markdown(endpoints, base_url)
            with open(md_path, "w", encoding="utf-8") as fh:
                fh.write(markdown)
            self.stdout.write(self.style.SUCCESS(f"Markdown written to {md_path}"))

        if "json" in formats:
            schema = self._generate_openapi(endpoints, base_url)
            with open(json_path, "w", encoding="utf-8") as fh:
                json.dump(schema, fh, indent=2)
            self.stdout.write(self.style.SUCCESS(f"OpenAPI JSON written to {json_path}"))

    # ------------------------------------------------------------------
    def _gather_endpoints(self) -> Iterable[Dict[str, Any]]:
        resolver = get_resolver()

        def walk(patterns, prefix=""):
            for pattern in patterns:
                try:
                    if isinstance(pattern, URLResolver):
                        new_prefix = self._join(prefix, pattern.pattern.describe())
                        yield from walk(pattern.url_patterns, new_prefix)
                    elif isinstance(pattern, URLPattern):
                        path = self._join(prefix, pattern.pattern.describe())
                        callback = pattern.callback
                        yield self._inspect_callback(path, pattern.name, callback)
                except Exception as exc:  # pragma: no cover
                    self.stderr.write(f"Failed processing pattern {pattern}: {exc}")

        yield from walk(resolver.url_patterns)

    def _join(self, prefix: str, route: str) -> str:
        parts = [prefix.strip("/"), route.strip("/")]
        path = "/" + "/".join([p for p in parts if p])
        if not path.endswith("/"):
            path += "/"
        return path

    def _qualname(self, obj: Any) -> str:
        return f"{obj.__module__}.{obj.__name__}" if hasattr(obj, "__name__") else str(obj)

    def _inspect_callback(self, path: str, name: Optional[str], callback: Any) -> Dict[str, Any]:
        view = getattr(callback, "view_class", None) or getattr(callback, "cls", None) or callback

        methods: List[str] = []
        try:
            if hasattr(callback, "actions"):
                methods = [m.upper() for m in callback.actions.keys()]
            elif hasattr(view, "http_method_names"):
                methods = [m.upper() for m in getattr(view, "http_method_names", []) if m]
            elif hasattr(callback, "allowed_methods"):
                methods = list(callback.allowed_methods)
        except Exception:
            pass
        if not methods:
            methods = ["GET", "POST"]

        doc = inspect.getdoc(view) or ""
        summary = ""
        description = ""
        if doc:
            lines = doc.strip().splitlines()
            summary = lines[0]
            description = "\n".join(lines[1:]).strip()

        permissions = [self._qualname(p) for p in getattr(view, "permission_classes", []) or []]
        throttles = [self._qualname(t) for t in getattr(view, "throttle_classes", []) or []]
        serializer = None
        ser = getattr(view, "serializer_class", None)
        if ser:
            serializer = self._qualname(ser)

        module = getattr(view, "__module__", "")
        app = module.split(".")[0]

        return {
            "path": path,
            "name": name,
            "methods": methods,
            "view": self._qualname(view),
            "docstring": summary,
            "description": description,
            "permissions": permissions,
            "throttles": throttles,
            "serializer": serializer,
            "app": app,
        }

    # ------------------------------------------------------------------
    def _render_markdown(self, endpoints: List[Dict[str, Any]], base_url: str) -> str:
        by_app: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for ep in endpoints:
            by_app[ep["app"]].append(ep)

        lines = ["# API Endpoints", f"_Generated {datetime.utcnow().isoformat()}_", ""]
        lines.append("## Summary")
        for app in sorted(by_app):
            lines.append(f"- [{app}](#{app})")
        for app in sorted(by_app):
            lines.append("")
            lines.append(f"## {app}")
            for ep in sorted(by_app[app], key=lambda e: e["path"]):
                methods = ", ".join(ep["methods"])
                header = f"`{ep['path']}` • {methods}"
                if ep["name"]:
                    header += f" • {ep['name']}"
                lines.append(f"### {header}")
                lines.append(f"- View: `{ep['view']}`")
                if ep["permissions"]:
                    lines.append(f"- Permissions: {', '.join(ep['permissions'])}")
                if ep["throttles"]:
                    lines.append(f"- Throttles: {', '.join(ep['throttles'])}")
                if ep["serializer"]:
                    lines.append(f"- Serializer: `{ep['serializer']}`")
                if ep["docstring"]:
                    lines.append(f"- Doc: {ep['docstring']}")
                curl_example = f"curl -X {ep['methods'][0]} '{base_url}{ep['path']}' -H 'Accept: application/json'"
                lines.append("```bash")
                lines.append(curl_example)
                lines.append("```")
        return "\n".join(lines) + "\n"

    def _generate_openapi(self, endpoints: List[Dict[str, Any]], base_url: str) -> Dict[str, Any]:
        title = getattr(settings, "PROJECT_NAME", settings.ROOT_URLCONF.split(".")[0])
        schema = None

        try:  # pragma: no cover
            from drf_spectacular.generators import SchemaGenerator

            generator = SchemaGenerator()
            schema = generator.get_schema(request=None, public=True)
            if hasattr(schema, "to_dict"):
                schema = schema.to_dict()
        except Exception:
            schema = None

        if schema is None and "drf_yasg" in settings.INSTALLED_APPS:
            try:  # pragma: no cover
                from drf_yasg.generators import OpenAPISchemaGenerator
                from drf_yasg import openapi

                info = openapi.Info(title=title, default_version="0.1.0")
                generator = OpenAPISchemaGenerator(info)
                swag = generator.get_schema(request=None, public=True)
                schema = swag.as_odict()
            except Exception:
                schema = None

        if schema is not None:
            return schema

        paths: Dict[str, Any] = {}
        for ep in endpoints:
            path_item = paths.setdefault(ep["path"], {})
            for method in ep["methods"]:
                path_item[method.lower()] = {
                    "summary": ep["docstring"],
                    "description": ep["description"],
                    "responses": {"200": {"description": "OK"}},
                }

        return {
            "openapi": "3.0.0",
            "info": {"title": title, "version": "0.1.0"},
            "servers": [{"url": base_url}],
            "paths": paths,
        }
