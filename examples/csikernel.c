#include <linux/module.h>
#include <linux/connector.h>
#include <linux/timer.h>

#define CN_IDX_IWLAGN   (CN_NETLINK_USERS + 0xf)
#define CN_VAL_IWLAGN   0x1

static struct cb_id cn_ck_id = {CN_IDX_IWLAGN, CN_VAL_IWLAGN};
static struct sock *nls;
static char cn_ck_name[] = "cn_ck";
static struct timer_list cn_ck_timer;

static void cn_ck_callback(struct cn_msg *msg, struct netlink_skb_parms *skb){
	pr_info("%s: %lu: idx=%x, val=%x, seq=%u, ack=%u, len=%d; %s. \n",
		__func__, jiffies, msg->id.idx, msg->id.val, msg->seq, msg->ack, msg->len,
		msg->len ? (char*)msg->data : "");
}

static u32 cn_ck_timer_count;
static void cn_ck_timer_func(struct timer_list *unused){
	struct cn_msg *m;
	char data[32];

	m = kzalloc(sizeof(*m) + sizeof(data), GFP_ATOMIC);
	if (m){
		memcpy(&m->id, &cn_ck_id, sizeof(m->id));
		m->seq = cn_ck_timer_count;
		m->len = sizeof(data);
		m->len = scnprintf(data, sizeof(data), "counter = %u", cn_ck_timer_count) + 1;

		memcpy(m + 1, data, m->len);
		cn_netlink_send(m, 0, 0, GFP_ATOMIC);
		kfree(m);
	}
	cn_ck_timer_count++;
	mod_timer(&cn_ck_timer, jiffies + msecs_to_jiffies(1000));
}

int __init cn_ck_init(void){
	int err;

	err = cn_add_callback(&cn_ck_id, cn_ck_name, cn_ck_callback);
	if (err) {
		if (nls && nls->sk_socket)
			sock_release(nls->sk_socket);
	}

	timer_setup(&cn_ck_timer, cn_ck_timer_func, 0);
	mod_timer(&cn_ck_timer, jiffies + msecs_to_jiffies(1000));
	pr_info("\033[33mcsikernel\033[0m: initialized with id={%u.%u}\n", cn_ck_id.idx, cn_ck_id.val);
	return 0;
}

void __exit cn_ck_exit(void){
	del_timer_sync(&cn_ck_timer);
	cn_del_callback(&cn_ck_id);
	if (nls && nls->sk_socket)
		sock_release(nls->sk_socket);
	pr_info("\033[33mcsikernel\033[0m: removed ok\n");
}

module_init(cn_ck_init);
module_exit(cn_ck_exit);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("send message from kernel to userspace");
MODULE_AUTHOR("suhecheng");
