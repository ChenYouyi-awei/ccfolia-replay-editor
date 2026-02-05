#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云TTS代理服务器 (Python版本)
用于解决浏览器CORS跨域问题

使用方法：
1. 在命令行运行: python aliyun-tts-proxy.py
2. 服务器会在 http://localhost:3000 启动
3. 保持窗口打开，然后使用编辑器
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
from datetime import datetime

PORT = 3000
ALIYUN_ENDPOINT = 'nls-gateway-cn-shanghai.aliyuncs.com'

class ProxyHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """自定义日志格式"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {format % args}")

    def do_OPTIONS(self):
        """处理OPTIONS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """处理GET请求"""
        if self.path.startswith('/tts'):
            # 提取查询参数
            query_string = self.path.split('?', 1)[1] if '?' in self.path else ''
            
            # 构建阿里云API URL
            aliyun_url = f'https://{ALIYUN_ENDPOINT}/stream/v1/tts?{query_string}'
            
            # 显示简短的日志
            short_path = self.path[:100] + '...' if len(self.path) > 100 else self.path
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 转发请求: {short_path}")
            
            try:
                # 发起请求到阿里云
                req = urllib.request.Request(aliyun_url)
                req.add_header('User-Agent', 'Mozilla/5.0')
                
                with urllib.request.urlopen(req) as response:
                    content_type = response.headers.get('Content-Type', 'application/octet-stream')
                    status_code = response.status
                    data = response.read()
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 响应状态: {status_code}, Content-Type: {content_type}, 大小: {len(data)} bytes")
                    
                    # 发送响应
                    self.send_response(status_code)
                    self.send_header('Content-Type', content_type)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Content-Length', len(data))
                    self.end_headers()
                    self.wfile.write(data)
                    
            except urllib.error.HTTPError as e:
                # HTTP错误（如400, 401等）
                error_data = e.read()
                print(f"[{datetime.now().strftime('%H:%M:%S')}] HTTP错误: {e.code} {e.reason}")
                
                self.send_response(e.code)
                self.send_header('Content-Type', e.headers.get('Content-Type', 'application/json'))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(error_data)
                
            except Exception as e:
                # 其他错误
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 请求失败: {str(e)}")
                
                error_msg = f'{{"error": "代理服务器错误: {str(e)}"}}'.encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(error_msg)
        else:
            # 其他路径返回404
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            msg = '404 Not Found\n\n使用方法: http://localhost:3000/tts?appkey=xxx&token=xxx&text=xxx...'
            self.wfile.write(msg.encode('utf-8'))

def run_server():
    """启动服务器"""
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, ProxyHandler)
    
    print('=' * 60)
    print('阿里云TTS代理服务器已启动！')
    print('=' * 60)
    print(f'监听端口: http://localhost:{PORT}')
    print(f'代理目标: https://{ALIYUN_ENDPOINT}')
    print()
    print('现在可以在浏览器中打开 ccfolia-replay-editor.html 文件了')
    print('按 Ctrl+C 停止服务器')
    print('=' * 60)
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n')
        print('=' * 60)
        print('服务器已停止')
        print('=' * 60)
        httpd.shutdown()

if __name__ == '__main__':
    run_server()
