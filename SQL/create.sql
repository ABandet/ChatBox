CREATE TABLE users (
    id integer NOT NULL PRIMARY KEY,
    username varchar(15) NOT NULL CONSTRAINT username_len_min_3 CHECK (LENGTH(username) >= 3),
    password varchar(155) NOT NULL,
    nb_messages integer DEFAULT 10,
    txt_color varchar(7) DEFAULT 0,
    grade integer DEFAULT 0
);

CREATE SEQUENCE users_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

ALTER SEQUENCE users_id_seq OWNED BY users.id;

CREATE TABLE messages (
    id integer NOT NULL PRIMARY KEY,
    user_id integer NOT NULL,
    message text NOT NULL,
    "timestamp" timestamp without time zone DEFAULT now(),
    CONSTRAINT messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE SEQUENCE messages_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

ALTER SEQUENCE messages_id_seq OWNED BY messages.id;

CREATE TABLE discussions (
  id integer NOT NULL PRIMARY KEY,
  sender_id integer NOT NULL,
  receiver_id integer NOT NULL,
  message text NOT NULL,
  "timestamp" timestamp without time zone DEFAULT now(),
  CONSTRAINT messages_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES users(id),
  CONSTRAINT messages_receiver_id_fkey FOREIGN KEY (receiver_id) REFERENCES users(id)
);

CREATE SEQUENCE discussions_id_seq
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;

ALTER SEQUENCE discussions_id_seq OWNED BY discussions.id;

ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq'::regclass);
ALTER TABLE messages ALTER COLUMN id SET DEFAULT nextval('messages_id_seq'::regclass);
ALTER TABLE discussions ALTER COLUMN id SET DEFAULT nextval('discussions_id_seq'::regclass);
