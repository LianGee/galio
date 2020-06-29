# Galio

`galio` 是一款针对在`k8s`上发布应用的工具。`galio`支持模板式发布，您可以设定好模板后，`galio`会通过模板构建相应的发布信息，通过`api`进行发布。

## 功能  

1. 构建
2. 发布
3. 数据库查询

## 开发进度  
- [x] 使用镜像中心
- [x] project 跳转build和deploy
- [x] 移除k8s无用代码
- [x] deploy log
- [x] read log 使用watch模式
- [x] build log 增加uuid
- [x] 移除socket无用日志 (非debug模式可关闭日志)
- [ ] 项目配置表单增加域名，支持修改，默认使用根域名绑定
- [ ] 日志权限，socket权限排查
- [x] 日志追踪
- [ ] 发布环境变量以及启动命令设置
- [x] 日志下载
- [x] build重构
- [x] template预览
- [ ] nginx rule name 必填
- [ ] 各类table提供搜索，分页
- [ ] npm、gradle、mvn、jdk、python版本
- [ ] 编译速度优化
