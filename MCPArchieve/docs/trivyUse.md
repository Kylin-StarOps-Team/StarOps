#  使用方法

# Trivy 扫描目标与命令用法汇总

| 扫描目标             | 使用命令          | 命令示例                                                     |
| -------------------- | ----------------- | ------------------------------------------------------------ |
| 容器镜像             | trivy image       | `trivy image nginx:alpine`                                   |
| 本地文件系统/项目    | trivy fs          | `trivy fs .` <br> `trivy fs /path/to/project`                |
| Git 仓库             | trivy repo        | `trivy repo https://github.com/aquasecurity/trivy`           |
| Kubernetes 集群      | trivy k8s         | `trivy k8s cluster` <br> `trivy k8s --namespace default`     |
| 配置文件 (IaC)       | trivy config      | `trivy config ./terraform/` <br> `trivy config ./k8s/`       |
| 软件物料清单（SBOM） | trivy sbom        | `trivy sbom sbom.spdx.json` <br> `trivy sbom sbom.cyclonedx.json` |
| 敏感信息泄露         | trivy fs + secret | `trivy fs --scanners secret .`                               |
| Dockerfile 检查      | trivy config      | `trivy config Dockerfile`                                    |
| Helm Chart 检查      | trivy config      | `trivy config ./helm-chart/`                                 |

# 额外说明

- 输出可添加 `-f json -o output.json` 输出为 JSON 格式

# Trivy 各扫描目标的主要检测内容与缺陷类型

| 扫描目标             | 命令                | 主要检测内容                                                 | 可发现的缺陷类型                                             |
| -------------------- | ------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 容器镜像             | `trivy image`       | 扫描容器镜像中的系统包、语言依赖、配置                       | ✅ 已知漏洞（CVE）<br>✅ 应用依赖漏洞（pip/npm/maven等）<br>✅ 系统包漏洞<br>✅ 漏洞修复状态 |
| 本地文件系统/项目    | `trivy fs`          | 扫描源码目录中的依赖、配置、Secrets 等                       | ✅ 应用依赖漏洞<br>✅ 敏感信息（如密码、API 密钥）<br>✅ 配置风险（如 Dockerfile 错误） |
| Git 仓库             | `trivy repo`        | 拉取远程代码并进行 fs/config 等扫描                          | ✅ 同本地项目一样的依赖漏洞<br>✅ IaC 配置缺陷<br>✅ 明文密钥泄露等 |
| Kubernetes 集群      | `trivy k8s`         | 扫描 K8s 资源对象（Pod、RBAC、Deployment 等）                | ✅ 不安全配置（如容器运行为 root）<br>✅ 镜像漏洞<br>✅ 暴露服务/权限配置问题 |
| 配置文件 (IaC)       | `trivy config`      | 扫描 IaC 文件（Terraform、Kubernetes YAML、Dockerfile、Helm Chart） | ✅ 不合规配置（如 S3 桶公有）<br>✅ 安全基准（如 CIS Benchmark）<br>✅ 弱权限配置等 |
| 软件物料清单（SBOM） | `trivy sbom`        | 扫描 CycloneDX/SPDX 生成的 SBOM 清单文件中列出的依赖         | ✅ SBOM 中依赖项的已知漏洞（CVE）                             |
| 敏感信息泄露         | `--scanners secret` | 检查源码/配置中的机密信息                                    | ✅ 明文密码<br>✅ API Token<br>✅ AWS 密钥<br>✅ SSH 私钥等      |
| Dockerfile 检查      | `trivy config`      | 检查 Dockerfile 是否存在不安全指令                           | ✅ 使用 root 用户<br>✅ 不加版本 tag 的基础镜像<br>✅ 未清理缓存层等 |