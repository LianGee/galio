create table if not exists galio.db_inst
(
  id         bigint(11) auto_increment comment '主键'
    primary key,
  created_at bigint(11)             null comment '创建时间',
  updated_at bigint(11)             null comment '更新时间',
  is_delete  tinyint(3)  default 0  null comment '是否删除'
)
  comment '数据库实例' charset = utf8mb4;

create index idx_created_at
  on galio.build_log (created_at);

create index idx_is_delete
  on galio.build_log (is_delete);

create index idx_updated_at
  on galio.build_log (updated_at);

