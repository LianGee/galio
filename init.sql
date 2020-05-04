create table if not exists galio.cloud_host
(
  id         bigint(11) auto_increment comment '主键'
    primary key,
  created_at bigint(11)             null comment '创建时间',
  updated_at bigint(11)             null comment '更新时间',
  is_delete  tinyint(3)  default 0  null comment '是否删除'
)
  comment '数据库实例' charset = utf8mb4;

create index idx_created_at
  on galio.cloud_host (created_at);

create index idx_is_delete
  on galio.cloud_host (is_delete);

create index idx_updated_at
  on galio.cloud_host (updated_at);

