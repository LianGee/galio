create table if not exists galio.cloud_host
(
  id         bigint(11) auto_increment comment '����'
    primary key,
  created_at bigint(11)             null comment '����ʱ��',
  updated_at bigint(11)             null comment '����ʱ��',
  is_delete  tinyint(3)  default 0  null comment '�Ƿ�ɾ��'
)
  comment '���ݿ�ʵ��' charset = utf8mb4;

create index idx_created_at
  on galio.cloud_host (created_at);

create index idx_is_delete
  on galio.cloud_host (is_delete);

create index idx_updated_at
  on galio.cloud_host (updated_at);

