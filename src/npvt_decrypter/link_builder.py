"""
Converting decrypted output to standard link include:
trojan://, vless://, vmess://
"""
import base64
import json
import urllib.parse

_KNOWN_PROTOCOLS = ("trojan", "vless", "vmess")


def _build_network_extras(stream_settings):
    network = stream_settings.get("network", "tcp")
    security = stream_settings.get("security", "none")
    extra = {"type": network, "security": security}

    if network == "ws":
        ws = stream_settings.get("wsSettings", {}) or {}
        if ws.get("path"):
            extra["path"] = ws["path"]
        host = (ws.get("headers", {}) or {}).get("Host")
        if host:
            extra["host"] = host

    if security == "tls":
        tls = stream_settings.get("tlsSettings", {}) or {}
        if tls.get("serverName"):
            extra["sni"] = tls["serverName"]
        if tls.get("fingerprint"):
            extra["fp"] = tls["fingerprint"]
        if tls.get("alpn"):
            extra["alpn"] = ",".join(tls["alpn"])
        extra["allowInsecure"] = "1" if tls.get("allowInsecure") else "0"

    return network, security, extra


def _outbound_to_link(outbound, remark):
    proto = str(outbound.get("protocol", "")).lower()
    settings = outbound.get("settings", {}) or {}
    stream = outbound.get("streamSettings", {}) or {}
    network, security, extra = _build_network_extras(stream)
    remark_q = urllib.parse.quote(str(remark))

    if proto == "trojan":
        srv = (settings.get("servers") or [{}])[0]
        server, port = srv.get("address"), srv.get("port")
        if not server or not port:
            return None
        password = srv.get("password", "")
        qs = urllib.parse.urlencode(extra)
        return f"trojan://{password}@{server}:{port}?{qs}#{remark_q}"

    if proto == "vless":
        vnext = (settings.get("vnext") or [{}])[0]
        server, port = vnext.get("address"), vnext.get("port")
        if not server or not port:
            return None
        user = (vnext.get("users") or [{}])[0]
        uuid = user.get("id", "")
        qs = urllib.parse.urlencode(extra)
        return f"vless://{uuid}@{server}:{port}?{qs}#{remark_q}"

    if proto == "vmess":
        vnext = (settings.get("vnext") or [{}])[0]
        server, port = vnext.get("address"), vnext.get("port")
        if not server or not port:
            return None
        user = (vnext.get("users") or [{}])[0]
        vmess_dict = {
            "v": "2", "ps": str(remark), "add": str(server), "port": str(port),
            "id": user.get("id", ""), "aid": str(user.get("alterId", 0)),
            "scy": "auto", "net": network, "type": "none",
            "host": extra.get("host", ""), "path": extra.get("path", ""),
            "tls": security, "sni": extra.get("sni", ""),
        }
        b64_str = base64.b64encode(json.dumps(vmess_dict).encode("utf-8")).decode("utf-8")
        return f"vmess://{b64_str}"

    return None


def _legacy_profile_to_link(profile, item, remark):
    remark_q = urllib.parse.quote(str(remark))

    server = profile.get("server") or profile.get("address") or profile.get("host") or profile.get("add")
    port = profile.get("serverPort") or profile.get("port")
    if not server or not port:
        return None

    proto = str(profile.get("protocol") or profile.get("type") or item.get("type") or "").lower()
    network = profile.get("network") or profile.get("net") or "tcp"
    path = profile.get("path") or ""
    host = profile.get("host") or ""
    sni = profile.get("sni") or host
    security = profile.get("security") or "tls"
    alpn = profile.get("alpn") or ""
    fp = profile.get("fingerPrint") or profile.get("fp") or ""
    insecure = profile.get("insecure", False)

    def build_query(extra=None):
        q = {"type": network, "security": security}
        if sni:
            q["sni"] = sni
        if path:
            q["path"] = path
        if host:
            q["host"] = host
        if alpn:
            q["alpn"] = alpn
        if fp:
            q["fp"] = fp
        if extra:
            q.update(extra)
        return urllib.parse.urlencode(q)

    if "trojan" in proto or ("password" in profile and "uuid" not in profile and "id" not in profile):
        password = profile.get("password") or ""
        qs = build_query({"allowInsecure": "1" if insecure else "0"})
        return f"trojan://{password}@{server}:{port}?{qs}#{remark_q}"

    if "vless" in proto or "uuid" in profile or "flow" in profile:
        uuid = profile.get("uuid") or profile.get("id") or ""
        qs = build_query()
        return f"vless://{uuid}@{server}:{port}?{qs}#{remark_q}"

    if "vmess" in proto or "id" in profile:
        vmess_dict = {
            "v": "2", "ps": str(remark), "add": str(server), "port": str(port),
            "id": str(profile.get("uuid") or profile.get("id") or ""),
            "aid": str(profile.get("alterId", 0)), "scy": "auto",
            "net": str(network), "type": "none", "host": str(host),
            "path": str(path), "tls": str(security or "none"), "sni": str(sni),
        }
        b64_str = base64.b64encode(json.dumps(vmess_dict).encode("utf-8")).decode("utf-8")
        return f"vmess://{b64_str}"

    return None


def item_to_links(item):
    profile = item.get("v2rayProfile") if isinstance(item.get("v2rayProfile"), dict) else item
    remark = (
        profile.get("remarks") or profile.get("remark") or profile.get("ps")
        or item.get("name") or "NPVT-Extracted"
    )

    links = []
    v2ray_json_str = item.get("v2rayJson") or profile.get("v2rayJson")
    if v2ray_json_str:
        try:
            vjson = json.loads(v2ray_json_str)
            for ob in vjson.get("outbounds", []):
                if str(ob.get("protocol", "")).lower() in _KNOWN_PROTOCOLS:
                    link = _outbound_to_link(ob, remark)
                    if link:
                        links.append(link)
        except (json.JSONDecodeError, TypeError, KeyError):
            pass

    if links:
        return links

    link = _legacy_profile_to_link(profile, item, remark)
    return [link] if link else []


def extract_links_from_json(data_input):
    if isinstance(data_input, (bytes, str)):
        try:
            data = json.loads(data_input)
        except (json.JSONDecodeError, TypeError):
            return []
    else:
        data = data_input

    items = data if isinstance(data, list) else [data]
    links = []
    for item in items:
        if isinstance(item, dict):
            links.extend(item_to_links(item))
    return links
