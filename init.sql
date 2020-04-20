create table if not exists galio.db_inst
(
  id         bigint(11) auto_increment comment '����'
    primary key,
  created_at bigint(11)             null comment '����ʱ��',
  updated_at bigint(11)             null comment '����ʱ��',
  is_delete  tinyint(3)  default 0  null comment '�Ƿ�ɾ��'
)
  comment '���ݿ�ʵ��' charset = utf8mb4;

create index idx_created_at
  on galio.build_log (created_at);

create index idx_is_delete
  on galio.build_log (is_delete);

create index idx_updated_at
  on galio.build_log (updated_at);

