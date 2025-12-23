import argparse
import concurrent.futures
import json
import os
import socket
import re
import requests
import urllib3
from urllib.parse import urlparse
from datetime import datetime

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 漏洞检测函数
class VulnerabilityScanner:
    def __init__(self, proxy=None, timeout=5):
        self.proxy = proxy
        self.timeout = timeout
        self.session = requests.Session()
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
        self.session.verify = False  # 忽略SSL证书验证
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # 服务检测器映射表
        self.detectors = {
            "ftp": self.check_ftp,
            "redis": self.check_redis,
            "docker": self.check_docker,
            "docker_registry": self.check_docker_registry,
            "elasticsearch": self.check_elasticsearch,
            "etcd": self.check_etcd,
            "jenkins": self.check_jenkins,
            "kibana": self.check_kibana,
            "zookeeper": self.check_zookeeper,
            "mongodb": self.check_mongodb,
            "kubernetes": self.check_kubernetes,
            "jupyter": self.check_jupyter,
            "nacos": self.check_nacos,
            "ollama": self.check_ollama,
            "rsync": self.check_rsync,
            "swagger": self.check_swagger,
            "springboot": self.check_springboot,
            "druid": self.check_druid,
            "ldap": self.check_ldap,
            "vnc": self.check_vnc,
            "couchdb": self.check_couchdb,
            "spark": self.check_spark,
            "weblogic": self.check_weblogic,
            "hadoop": self.check_hadoop,
            "jboss": self.check_jboss,
            "activemq": self.check_activemq,
            "zabbix": self.check_zabbix,
            "memcached": self.check_memcached,
            "rabbitmq": self.check_rabbitmq,
            "nfs": self.check_nfs,
            "dubbo": self.check_dubbo,
            "solr": self.check_solr,
            "harbor": self.check_harbor,
            "smb": self.check_smb,
            "wordpress": self.check_wordpress,
            "crowd": self.check_crowd,
            "uwsgi": self.check_uwsgi,
            "kong": self.check_kong,
            "thinkadmin": self.check_thinkadmin
        }
        
        # 服务默认端口映射
        self.default_ports = {
            "ftp": 21,
            "redis": 6379,
            "docker": 2375,
            "docker_registry": 5000,
            "elasticsearch": 9200,
            "etcd": 2379,
            "jenkins": 8080,
            "kibana": 5601,
            "zookeeper": 2181,
            "mongodb": 27017,
            "kubernetes": 8080,
            "jupyter": 8888,
            "nacos": 8848,
            "ollama": 11434,
            "rsync": 873,
            "swagger": None,
            "springboot": None,
            "druid": None,
            "ldap": 389,
            "vnc": 5900,
            "couchdb": 5984,
            "spark": 6066,
            "weblogic": 7001,
            "hadoop": 8088,
            "jboss": 8080,
            "activemq": 8161,
            "zabbix": 10051,
            "memcached": 11211,
            "rabbitmq": 15672,
            "nfs": 2049,
            "dubbo": 28096,
            "solr": 8983,
            "harbor": 80,
            "smb": 445,
            "wordpress": 80,
            "crowd": 8095,
            "uwsgi": 1717,
            "kong": 8001,
            "thinkadmin": 80
        }

        # nmap服务名称到检测器的映射
        self.nmap_service_mapping = {
            "ftp": "ftp",
            "redis": "redis",
            "docker": "docker",
            "http": ["swagger", "springboot", "druid", "wordpress", "thinkadmin", "harbor"],
            "https": ["swagger", "springboot", "druid", "wordpress", "thinkadmin", "harbor"],
            "elasticsearch": "elasticsearch",
            "etcd-client": "etcd",
            "etcd": "etcd",
            "jenkins": "jenkins",
            "kibana": "kibana",
            "zookeeper": "zookeeper",
            "mongodb": "mongodb",
            "kubernetes": "kubernetes",
            "jupyter": "jupyter",
            "nacos": "nacos",
            "ollama": "ollama",
            "rsync": "rsync",
            "ldap": "ldap",
            "vnc": "vnc",
            "couchdb": "couchdb",
            "spark": "spark",
            "weblogic": "weblogic",
            "hadoop": "hadoop",
            "jboss": "jboss",
            "activemq": "activemq",
            "zabbix-agent": "zabbix",
            "memcached": "memcached",
            "rabbitmq": "rabbitmq",
            "nfs": "nfs",
            "dubbo": "dubbo",
            "solr": "solr",
            "netbios-ssn": "smb",
            "microsoft-ds": "smb",
            "smb": "smb",
            "mysql": None,  # 暂不支持
            "ssh": None,    # 暂不支持
            "unknown": None  # 未知服务
        }

    def scan_target(self, target, services=None):
        """扫描单个目标的所有漏洞或指定服务"""
        # 解析目标
        parsed = urlparse(target)
        host = parsed.hostname if parsed.hostname else target
        port = parsed.port
        scheme = parsed.scheme or "http"

        target_info = {
            "host": host,
            "port": port,
            "scheme": scheme,
            "full_url": target
        }

        results = {"target": target, "vulnerabilities": []}

        # 确定要扫描的服务
        if services is None:
            services = list(self.detectors.keys())

        # 扫描所有指定服务
        for service in services:
            if port is None:
                default_port = self.default_ports.get(service)
                target_info["port"]=default_port
            status, message = self.detect_service(target_info, service)
            results["vulnerabilities"].append({
                "service": service,
                "status": status,
                "message": message
            })

        return results

    def scan_port_with_service(self, host, port, nmap_service=None):
        """
        扫描指定端口，支持基于nmap服务名的智能检测
        如果nmap识别的服务检测失败，会fallback到全量检测
        """
        results = {
            "host": host,
            "port": port,
            "nmap_service": nmap_service,
            "vulnerabilities": []
        }

        # 确定要测试的服务列表
        services_to_test = []

        if nmap_service and nmap_service.lower() in self.nmap_service_mapping:
            mapped = self.nmap_service_mapping[nmap_service.lower()]

            if mapped is None:
                print(f"[!] Service '{nmap_service}' on port {port} is not supported yet, will perform full scan")
                services_to_test = list(self.detectors.keys())
            elif isinstance(mapped, list):
                services_to_test = mapped
                print(f"[*] Testing port {port} ({nmap_service}) with services: {', '.join(mapped)}")
            else:
                services_to_test = [mapped]
                print(f"[*] Testing port {port} ({nmap_service}) with service: {mapped}")
        else:
            # 未知服务或未识别，使用全量检测
            if nmap_service and nmap_service.lower() != "unknown":
                print(f"[!] Unknown service '{nmap_service}' on port {port}, will perform full scan")
            else:
                print(f"[*] Port {port} service unknown, will perform full scan")
            services_to_test = list(self.detectors.keys())

        # 尝试检测
        need_fallback = False
        for service in services_to_test:
            target_info = {
                "host": host,
                "port": port,
                "scheme": "https" if port in [443, 8443] else "http",
                "full_url": f"http://{host}:{port}"
            }

            try:
                status, message = self.detect_service(target_info, service)
                results["vulnerabilities"].append({
                    "service": service,
                    "status": status,
                    "message": message
                })

                # 如果检测成功，不需要fallback
                if status:
                    print(f"[+] Found vulnerability: {service} on {host}:{port}")
                    need_fallback = False
                    break

            except Exception as e:
                # 如果是因为nmap识别的服务检测出错，标记需要fallback
                if nmap_service and len(services_to_test) == 1:
                    print(f"[!] Error testing {service} on {host}:{port}: {str(e)}, will fallback to full scan")
                    need_fallback = True
                    break

        # 如果需要fallback，进行全量检测
        if need_fallback and nmap_service:
            print(f"[*] Performing fallback full scan on {host}:{port}")
            all_services = list(self.detectors.keys())

            for service in all_services:
                # 跳过已经测试过的服务
                if service in services_to_test:
                    continue

                target_info = {
                    "host": host,
                    "port": port,
                    "scheme": "https" if port in [443, 8443] else "http",
                    "full_url": f"http://{host}:{port}"
                }

                try:
                    status, message = self.detect_service(target_info, service)
                    results["vulnerabilities"].append({
                        "service": service,
                        "status": status,
                        "message": message
                    })

                    if status:
                        print(f"[+] Found vulnerability in fallback scan: {service} on {host}:{port}")
                except Exception as e:
                    continue

        return results

    def detect_service(self, target_info, service_name):
        """检测指定服务是否存在未授权访问"""
        # 获取服务检测函数
        detector = self.detectors.get(service_name)
        if not detector:
            return False, f"Unsupported service: {service_name}"
        
        # 调用检测函数
        return detector(target_info)

    def check_ftp(self, target_info):
        """检测FTP未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 21)
        try:
            with socket.create_connection((host, port), timeout=self.timeout) as sock:
                sock.sendall(b"USER anonymous\r\n")
                response = sock.recv(1024).decode(errors="ignore")
                if "331" in response:
                    sock.sendall(b"PASS anonymous@example.com\r\n")
                    response = sock.recv(1024).decode(errors="ignore")
                    if "230" in response:
                        return True, "FTP anonymous login successful"
        except Exception as e:
            return False, f"FTP detection failed: {str(e)}"
        return False, "FTP unauthorized access not found"

    def check_redis(self, target_info):
        """检测Redis未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 6379)
        try:
            with socket.create_connection((host, port), timeout=self.timeout) as sock:
                sock.sendall(b"INFO\r\n")
                response = sock.recv(1024).decode(errors="ignore")
                if "redis_version" in response:
                    return True, "Redis unauthorized access"
        except Exception as e:
            return False, f"Redis detection failed: {str(e)}"
        return False, "Redis unauthorized access not found"

    def check_docker(self, target_info):
        """检测Docker未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 2375)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/version"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "ApiVersion" in response.text:
                return True, "Docker unauthorized access"
        except Exception as e:
            return False, f"Docker detection failed: {str(e)}"
        return False, "Docker unauthorized access not found"
    
    def check_docker_registry(self, target_info):
        """检测Docker Registry未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 5000)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/v2/_catalog"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "repositories" in response.text:
                return True, "Docker Registry unauthorized access"
        except Exception as e:
            return False, f"Docker Registry detection failed: {str(e)}"
        return False, "Docker Registry unauthorized access not found"

    def check_elasticsearch(self, target_info):
        """检测Elasticsearch未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 9200)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/_cat/indices"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "green" in response.text:
                return True, "Elasticsearch unauthorized access"
        except Exception as e:
            return False, f"Elasticsearch detection failed: {str(e)}"
        return False, "Elasticsearch unauthorized access not found"

    def check_etcd(self, target_info):
        """检测etcd未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 2379)
        scheme = target_info.get("scheme", "http")

        # 尝试多个etcd API端点
        endpoints = [
            ("/version", "etcdserver"),  # etcd版本信息
            ("/v2/keys", "node"),         # etcd v2 API
            ("/health", "health"),        # 健康检查端点
        ]

        for endpoint, keyword in endpoints:
            url = f"{scheme}://{host}:{port}{endpoint}"
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200 and keyword in response.text:
                    return True, f"etcd unauthorized access (endpoint: {endpoint})"
            except Exception:
                continue

        return False, "etcd unauthorized access not found"

    def check_jenkins(self, target_info):
        """检测Jenkins未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 8080)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/api/json"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "jobs" in response.text:
                return True, "Jenkins unauthorized access"
        except Exception as e:
            return False, f"Jenkins detection failed: {str(e)}"
        return False, "Jenkins unauthorized access not found"

    def check_kibana(self, target_info):
        """检测Kibana未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 5601)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/api/status"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "status" in response.text:
                return True, "Kibana unauthorized access"
        except Exception as e:
            return False, f"Kibana detection failed: {str(e)}"
        return False, "Kibana unauthorized access not found"

    def check_zookeeper(self, target_info):
        """检测Zookeeper未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 2181)
        try:
            with socket.create_connection((host, port), timeout=self.timeout) as sock:
                sock.sendall(b"stat\r\n")
                response = sock.recv(1024).decode(errors="ignore")
                if "Zookeeper version" in response:
                    return True, "Zookeeper unauthorized access"
        except Exception as e:
            return False, f"Zookeeper detection failed: {str(e)}"
        return False, "Zookeeper unauthorized access not found"

    def check_mongodb(self, target_info):
        """检测MongoDB未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 27017)
        try:
            with socket.create_connection((host, port), timeout=self.timeout) as sock:
                sock.sendall(b"db.adminCommand('ping')\r\n")
                response = sock.recv(1024).decode(errors="ignore")
                if "ok" in response:
                    return True, "MongoDB unauthorized access"
        except Exception as e:
            return False, f"MongoDB detection failed: {str(e)}"
        return False, "MongoDB unauthorized access not found"

    def check_kubernetes(self, target_info):
        """检测Kubernetes未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 8080)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/api/v1/namespaces/default/pods"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "items" in response.text:
                return True, "Kubernetes unauthorized access"
        except Exception as e:
            return False, f"Kubernetes detection failed: {str(e)}"
        return False, "Kubernetes unauthorized access not found"

    def check_jupyter(self, target_info):
        """检测Jupyter Notebook未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 8888)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/api/kernels"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "kernels" in response.text:
                return True, "Jupyter Notebook unauthorized access"
        except Exception as e:
            return False, f"Jupyter detection failed: {str(e)}"
        return False, "Jupyter unauthorized access not found"

    def check_nacos(self, target_info):
        """检测Nacos未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 8848)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/nacos/v1/auth/users?pageNo=1&pageSize=10"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "username" in response.text:
                return True, "Nacos unauthorized access"
        except Exception as e:
            return False, f"Nacos detection failed: {str(e)}"
        return False, "Nacos unauthorized access not found"

    def check_ollama(self, target_info):
        """检测Ollama未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 11434)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/api/tags"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "models" in response.text:
                return True, "Ollama unauthorized access"
        except Exception as e:
            return False, f"Ollama detection failed: {str(e)}"
        return False, "Ollama unauthorized access not found"

    def check_rsync(self, target_info):
        """检测Rsync未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 873)
        try:
            with socket.create_connection((host, port), timeout=self.timeout) as sock:
                sock.sendall(b"@RSYNCD: 31.0\n")
                response = sock.recv(1024).decode(errors="ignore")
                # 真正的rsync服务器应该返回以@RSYNCD:开头的响应，而不是HTML错误页面
                if response.strip().startswith("@RSYNCD:") and "<!DOCTYPE" not in response and "<html>" not in response.lower():
                    return True, "Rsync unauthorized access"
        except Exception as e:
            return False, f"Rsync detection failed: {str(e)}"
        return False, "Rsync unauthorized access not found"

    def check_swagger(self, target_info):
        """Swagger UI未授权访问检测"""
        host = target_info["host"]
        port = target_info.get("port", 80)
        scheme = target_info.get("scheme", "http")
        
        # 常见的Swagger UI路径
        paths = [
            "/swagger-ui.html",
            "/swagger/index.html",
            "/swagger/ui/index",
            "/swagger",
            "/api-docs",
            "/v2/api-docs",
            "/swagger-resources",
            "/swagger-ui",
            "/api/swagger-ui.html",
            "/docs",
            "/swagger-ui/index.html"
        ]
        
        # 尝试所有可能的路径
        for path in paths:
            url = f"{scheme}://{host}:{port}{path}" if port else f"{scheme}://{host}{path}"
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    # 使用更精确的识别方法
                    if any(keyword in response.text for keyword in ["Swagger UI", "swagger-ui", "swagger.json", "swagger.yaml"]):
                        return True, f"Swagger UI unauthorized access (path: {path})"
            except Exception:
                continue
        
        return False, "Swagger unauthorized access not found"

    def check_springboot(self, target_info):
        """检测SpringBoot Actuator未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 80)
        scheme = target_info.get("scheme", "http")
        
        # 常见的Actuator路径
        paths = [
            "/actuator",
            "/actuator/health",
            "/actuator/env",
            "/actuator/metrics",
            "/actuator/beans",
            "/actuator/mappings"
        ]
        
        for path in paths:
            url = f"{scheme}://{host}:{port}{path}" if port else f"{scheme}://{host}{path}"
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200 and "actuator" in response.text:
                    return True, f"SpringBoot Actuator unauthorized access (path: {path})"
            except Exception:
                continue
        
        return False, "SpringBoot unauthorized access not found"

    def check_druid(self, target_info):
        """检测Druid未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 80)
        scheme = target_info.get("scheme", "http")
        
        # 常见的Druid路径
        paths = [
            "/druid/index.html",
            "/druid/login.html",
            "/druid/weburi.html",
            "/druid/websession.html",
            "/druid/sql.html"
        ]
        
        for path in paths:
            url = f"{scheme}://{host}:{port}{path}" if port else f"{scheme}://{host}{path}"
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200 and "Druid" in response.text:
                    return True, f"Druid unauthorized access (path: {path})"
            except Exception:
                continue
        
        return False, "Druid unauthorized access not found"
    
    # 以下是新增的检测函数
    def check_ldap(self, target_info):
        """检测LDAP未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 389)
        try:
            with socket.create_connection((host, port), timeout=self.timeout) as sock:
                # LDAP匿名绑定尝试
                bind_request = bytes.fromhex("30 0c 02 01 01 60 07 02 01 03 04 00 80 00")
                sock.sendall(bind_request)
                response = sock.recv(1024)

                # 验证LDAP协议响应并解析BindResponse
                if response and len(response) >= 14 and response[0] == 0x30:
                    try:
                        idx = 2  # Skip SEQUENCE tag and length

                        # Skip MessageID (0x02 0x01 XX)
                        if idx < len(response) and response[idx] == 0x02:
                            idx += 3

                        # Check BindResponse (0x61)
                        if idx < len(response) and response[idx] == 0x61:
                            idx += 2  # Skip BindResponse tag and length

                            # Parse ResultCode (0x0a 0x01 XX)
                            if idx + 2 < len(response) and response[idx] == 0x0a and response[idx+1] == 0x01:
                                result_code = response[idx+2]
                                # Only report success if resultCode is 0x00
                                if result_code == 0x00:
                                    return True, "LDAP unauthorized access (anonymous bind successful)"
                    except IndexError:
                        pass
        except Exception as e:
            return False, f"LDAP detection failed: {str(e)}"
        return False, "LDAP unauthorized access not found"
    
    def check_vnc(self, target_info):
        """检测VNC未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 5900)
        try:
            with socket.create_connection((host, port), timeout=self.timeout) as sock:
                # 读取VNC协议响应
                response = sock.recv(1024)
                if b"RFB" in response:
                    return True, "VNC service exposed (possible unauthorized access)"
        except Exception as e:
            return False, f"VNC detection failed: {str(e)}"
        return False, "VNC unauthorized access not found"
    
    def check_couchdb(self, target_info):
        """检测CouchDB未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 5984)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/_all_dbs"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "[" in response.text:
                return True, "CouchDB unauthorized access"
        except Exception as e:
            return False, f"CouchDB detection failed: {str(e)}"
        return False, "CouchDB unauthorized access not found"
    
    def check_spark(self, target_info):
        """检测Apache Spark未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 6066)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "Spark" in response.text:
                return True, "Apache Spark unauthorized access"
        except Exception as e:
            return False, f"Apache Spark detection failed: {str(e)}"
        return False, "Apache Spark unauthorized access not found"
    
    def check_weblogic(self, target_info):
        """检测Weblogic未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 7001)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/console/login/LoginForm.jsp"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "WebLogic Server" in response.text:
                return True, "Weblogic console exposed (possible unauthorized access)"
        except Exception as e:
            return False, f"Weblogic detection failed: {str(e)}"
        return False, "Weblogic unauthorized access not found"
    
    def check_hadoop(self, target_info):
        """检测Hadoop YARN未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 8088)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/ws/v1/cluster/apps"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "apps" in response.text:
                return True, "Hadoop YARN unauthorized access"
        except Exception as e:
            return False, f"Hadoop detection failed: {str(e)}"
        return False, "Hadoop unauthorized access not found"
    
    def check_jboss(self, target_info):
        """检测JBoss未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 8080)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/jmx-console/"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "JBoss" in response.text:
                return True, "JBoss JMX console exposed (possible unauthorized access)"
        except Exception as e:
            return False, f"JBoss detection failed: {str(e)}"
        return False, "JBoss unauthorized access not found"
    
    def check_activemq(self, target_info):
        """检测ActiveMQ未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 8161)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/admin/"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "ActiveMQ" in response.text:
                return True, "ActiveMQ management console exposed (possible unauthorized access)"
        except Exception as e:
            return False, f"ActiveMQ detection failed: {str(e)}"
        return False, "ActiveMQ unauthorized access not found"
    
    def check_zabbix(self, target_info):
        """检测Zabbix未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 10051)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "Zabbix" in response.text:
                return True, "Zabbix service exposed (possible unauthorized access)"
        except Exception as e:
            return False, f"Zabbix detection failed: {str(e)}"
        return False, "Zabbix unauthorized access not found"
    
    def check_memcached(self, target_info):
        """检测Memcached未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 11211)
        try:
            with socket.create_connection((host, port), timeout=self.timeout) as sock:
                sock.sendall(b"stats\r\n")
                response = sock.recv(1024).decode(errors="ignore")
                if "STAT" in response:
                    return True, "Memcached unauthorized access"
        except Exception as e:
            return False, f"Memcached detection failed: {str(e)}"
        return False, "Memcached unauthorized access not found"
    
    def check_rabbitmq(self, target_info):
        """检测RabbitMQ未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 15672)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/api/overview"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "management_version" in response.text:
                return True, "RabbitMQ management API unauthorized access"
        except Exception as e:
            return False, f"RabbitMQ detection failed: {str(e)}"
        return False, "RabbitMQ unauthorized access not found"
    
    def check_nfs(self, target_info):
        """检测NFS未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 2049)
        try:
            with socket.create_connection((host, port), timeout=self.timeout) as sock:
                # 发送RPC NULL调用
                sock.sendall(b"\x80\x00\x00\x28\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x86\xa3\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
                response = sock.recv(1024)
                # 验证RPC响应格式：至少24字节，且为RPC Reply (消息类型1)
                if response and len(response) >= 24:
                    # 跳过fragment header(4字节)，检查RPC Reply标记
                    if len(response) >= 8:
                        # RPC消息类型应该是1 (Reply)
                        msg_type = int.from_bytes(response[4:8], byteorder='big')
                        if msg_type == 1:
                            return True, "NFS service exposed (possible unauthorized access)"
        except Exception as e:
            return False, f"NFS detection failed: {str(e)}"
        return False, "NFS unauthorized access not found"
    
    def check_dubbo(self, target_info):
        """检测Dubbo未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 28096)
        try:
            with socket.create_connection((host, port), timeout=self.timeout) as sock:
                sock.sendall(b"ls\r\n")
                response = sock.recv(1024).decode(errors="ignore")
                if "dubbo>" in response:
                    return True, "Dubbo console unauthorized access"
        except Exception as e:
            return False, f"Dubbo detection failed: {str(e)}"
        return False, "Dubbo unauthorized access not found"
    
    def check_solr(self, target_info):
        """检测Solr未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 8983)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/solr/admin/cores"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "responseHeader" in response.text:
                return True, "Solr unauthorized access"
        except Exception as e:
            return False, f"Solr detection failed: {str(e)}"
        return False, "Solr unauthorized access not found"
    
    def check_harbor(self, target_info):
        """检测Harbor未授权添加管理员漏洞"""
        host = target_info["host"]
        port = target_info.get("port", 80)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/api/v2.0/users"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "username" in response.text:
                return True, "Harbor user API exposed (possible unauthorized admin addition)"
        except Exception as e:
            return False, f"Harbor detection failed: {str(e)}"
        return False, "Harbor unauthorized access not found"
    
    def check_smb(self, target_info):
        """检测Windows共享未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 445)
        try:
            with socket.create_connection((host, port), timeout=self.timeout) as sock:
                # 发送SMB协商请求
                sock.sendall(b"\x00\x00\x00\x85\xff\x53\x4d\x42\x72\x00\x00\x00\x00\x18\x53\xc8")
                response = sock.recv(1024)
                # 验证SMB响应：检查SMB签名
                if response and len(response) >= 4:
                    # SMBv1: \xFFSMB 或 SMBv2/3: \xFESMB
                    if b"\xFF\x53\x4D\x42" in response[:10] or b"\xFE\x53\x4D\x42" in response[:10]:
                        return True, "SMB service exposed (possible unauthorized access)"
        except Exception as e:
            return False, f"SMB detection failed: {str(e)}"
        return False, "SMB unauthorized access not found"
    
    def check_wordpress(self, target_info):
        """检测WordPress未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 80)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/wp-admin/"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "WordPress" in response.text:
                return True, "WordPress admin panel exposed (possible unauthorized access)"
        except Exception as e:
            return False, f"WordPress detection failed: {str(e)}"
        return False, "WordPress unauthorized access not found"
    
    def check_crowd(self, target_info):
        """检测Atlassian Crowd未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 8095)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/crowd/admin/"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "Crowd" in response.text:
                return True, "Crowd management console exposed (possible unauthorized access)"
        except Exception as e:
            return False, f"Crowd detection failed: {str(e)}"
        return False, "Crowd unauthorized access not found"
    
    def check_uwsgi(self, target_info):
        """检测uWSGI未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 1717)
        try:
            with socket.create_connection((host, port), timeout=self.timeout) as sock:
                sock.sendall(b"add-mapping /foo /bar\n")
                response = sock.recv(1024).decode(errors="ignore")
                if "OK" in response:
                    return True, "uWSGI unauthorized access"
        except Exception as e:
            return False, f"uWSGI detection failed: {str(e)}"
        return False, "uWSGI unauthorized access not found"
    
    def check_kong(self, target_info):
        """检测Kong未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 8001)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "kong" in response.text:
                return True, "Kong management API exposed (possible unauthorized access)"
        except Exception as e:
            return False, f"Kong detection failed: {str(e)}"
        return False, "Kong unauthorized access not found"
    
    def check_thinkadmin(self, target_info):
        """检测ThinkAdmin未授权访问"""
        host = target_info["host"]
        port = target_info.get("port", 80)
        scheme = target_info.get("scheme", "http")
        url = f"{scheme}://{host}:{port}/admin.html"
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200 and "ThinkAdmin" in response.text:
                return True, "ThinkAdmin admin panel exposed (possible unauthorized access)"
        except Exception as e:
            return False, f"ThinkAdmin detection failed: {str(e)}"
        return False, "ThinkAdmin unauthorized access not found"

def parse_targets(target_input):
    """解析目标输入，支持多种格式"""
    targets = []

    # 如果是文件路径
    if os.path.isfile(target_input):
        with open(target_input, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    targets.append(line)
        return targets

    # 如果是逗号分隔的列表
    if ',' in target_input:
        return [t.strip() for t in target_input.split(',') if t.strip()]

    # 单个目标
    return [target_input]

def parse_nmap_result(nmap_file):
    """
    解析nmap扫描结果文件
    返回格式: [{"host": "192.168.1.1", "port": 80, "state": "open", "service": "http"}, ...]
    """
    targets = []
    current_host = None

    if not os.path.isfile(nmap_file):
        print(f"[!] Nmap result file not found: {nmap_file}")
        return targets

    with open(nmap_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()

            # 匹配主机行: Nmap scan report for 192.168.1.1
            host_match = re.search(r'Nmap scan report for (.+)', line)
            if host_match:
                current_host = host_match.group(1).strip()
                continue

            # 匹配端口行: 80/tcp    open     http
            # 格式: PORT      STATE    SERVICE
            port_match = re.match(r'^(\d+)/(tcp|udp)\s+(open|filtered|closed)\s+(.+)$', line)
            if port_match and current_host:
                port = int(port_match.group(1))
                protocol = port_match.group(2)
                state = port_match.group(3)
                service = port_match.group(4).strip()

                # 只处理open和filtered状态的端口
                if state in ['open', 'filtered']:
                    targets.append({
                        "host": current_host,
                        "port": port,
                        "protocol": protocol,
                        "state": state,
                        "service": service
                    })

    print(f"[*] Parsed {len(targets)} ports from nmap result")
    return targets

def main():
    parser = argparse.ArgumentParser(description="Unauthorized access vulnerability scanner")
    parser.add_argument("-u", "--url", help="Single target URL or multiple targets (comma separated)")
    parser.add_argument("-f", "--file", help="File containing multiple targets")
    parser.add_argument("-n", "--nmap", help="Nmap scan result file")
    parser.add_argument("-s", "--services", help="Specify services to scan (comma separated)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads (default: 10)")
    parser.add_argument("--proxy", help="Proxy settings (e.g., http://127.0.0.1:8080)")
    parser.add_argument("--out", help="Output file path")

    args = parser.parse_args()

    if not args.url and not args.file and not args.nmap:
        parser.print_help()
        print("\nError: Must provide -u/--url, -f/--file, or -n/--nmap parameter")
        return

    scanner = VulnerabilityScanner(proxy=args.proxy)
    results = []

    # Nmap模式：解析nmap结果并扫描
    if args.nmap:
        print(f"[*] Parsing nmap result file: {args.nmap}")
        nmap_targets = parse_nmap_result(args.nmap)

        if not nmap_targets:
            print("[!] No valid targets found in nmap result")
            return

        print(f"[*] Starting scan for {len(nmap_targets)} ports using {args.threads} threads")

        # 使用线程池执行扫描
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
            future_to_target = {
                executor.submit(scanner.scan_port_with_service, t["host"], t["port"], t["service"]): t
                for t in nmap_targets
            }

            for future in concurrent.futures.as_completed(future_to_target):
                target = future_to_target[future]
                try:
                    result = future.result()
                    results.append(result)

                    # 打印检测到漏洞的结果
                    vulnerable = [v for v in result["vulnerabilities"] if v["status"]]
                    if vulnerable:
                        print(f"\n[+] Vulnerabilities found on {result['host']}:{result['port']}")
                        for vuln in vulnerable:
                            print(f"    - {vuln['service']}: {vuln['message']}")
                except Exception as e:
                    print(f"[-] Scan failed for {target['host']}:{target['port']}, error: {str(e)}")

    # 传统模式：URL/文件扫描
    else:
        # 解析目标
        targets = []
        if args.url:
            targets.extend(parse_targets(args.url))
        if args.file:
            targets.extend(parse_targets(args.file))

        # 去重
        targets = list(set(targets))

        # 解析要扫描的服务
        services = None
        if args.services:
            services = [s.strip().lower() for s in args.services.split(',')]
            valid_services = set(scanner.detectors.keys())
            invalid_services = set(services) - valid_services

            if invalid_services:
                print(f"Warning: The following services are not supported and will be ignored: {', '.join(invalid_services)}")
                services = list(set(services) - invalid_services)

        print(f"[*] Starting scan for {len(targets)} targets using {args.threads} threads")
        if services:
            print(f"[*] Specified services: {', '.join(services)}")

        # 使用线程池执行扫描
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
            future_to_target = {executor.submit(scanner.scan_target, target, services): target for target in targets}

            for future in concurrent.futures.as_completed(future_to_target):
                target = future_to_target[future]
                try:
                    result = future.result()
                    results.append(result)
                    # 打印结果
                    print(f"\n[+] Scan completed: {target}")
                    for vuln in result["vulnerabilities"]:
                        status = "Vulnerable" if vuln["status"] else "Secure"
                        print(f"  - {vuln['service']}: {status} ({vuln['message']})")
                except Exception as e:
                    print(f"[-] Scan failed: {target}, error: {str(e)}")

    # 输出结果到文件
    if args.out:
        output_format = os.path.splitext(args.out)[1].lower()
        if output_format == ".json":
            with open(args.out, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n[*] Results saved as JSON file: {args.out}")
        else:
            with open(args.out, 'w') as f:
                f.write("Unauthorized Access Vulnerability Scan Report\n")
                f.write(f"Scan time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total targets scanned: {len(results)}\n\n")

                for result in results:
                    if "target" in result:  # 传统模式
                        f.write(f"Target: {result['target']}\n")
                        for vuln in result["vulnerabilities"]:
                            status = "Vulnerable" if vuln["status"] else "Secure"
                            f.write(f"  - {vuln['service']}: {status} ({vuln['message']})\n")
                    else:  # Nmap模式
                        f.write(f"Host: {result['host']}:{result['port']} (Nmap service: {result.get('nmap_service', 'unknown')})\n")
                        vulnerable = [v for v in result["vulnerabilities"] if v["status"]]
                        if vulnerable:
                            for vuln in vulnerable:
                                f.write(f"  [!] {vuln['service']}: {vuln['message']}\n")
                        else:
                            f.write(f"  [-] No vulnerabilities found\n")
                    f.write("\n")
            print(f"\n[*] Results saved as text file: {args.out}")

    print("\n[+] Scan completed")

if __name__ == "__main__":
    main()
