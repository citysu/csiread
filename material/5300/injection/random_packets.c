#include <linux/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>

#include <tx80211.h>
#include <tx80211_packet.h>

#include "util.h"

#define PAYLOAD_SIZE	2000000

static void init_lorcon();
static void handle();
static void timerThread();

struct lorcon_packet
{
	__le16	fc;
	__le16	dur;
	u_char	addr1[6];
	u_char	addr2[6];
	u_char	addr3[6];
	__le16	seq;
	u_char	payload[0];
} __attribute__ ((packed));

struct tx80211			tx;
struct tx80211_packet	tx_packet;
struct lorcon_packet 	*packet;

uint8_t 				*payload_buffer;
int32_t 				ret;
uint32_t 				i;

uint32_t 				num_packets;
uint32_t 				packet_size;	
uint32_t 				mode;
uint32_t 				delay_us;

static inline void payload_memcpy(uint8_t *dest, uint32_t length, uint32_t offset)
{
	uint32_t i;
	for (i = 0; i < length; ++i) {
		dest[i] = payload_buffer[(offset + i) % PAYLOAD_SIZE];
	}
}

int main(int argc, char** argv)
{
	/* Parse arguments */
	if (argc > 5) {
		printf("Usage: random_packets <number> <length> <mode: 0=my MAC, 1=injection MAC> <delay in us>\n");
		return 1;
	}
	if (argc < 5 || (1 != sscanf(argv[4], "%u", &delay_us))) {
		delay_us = 0;
	}
	if (argc < 4 || (1 != sscanf(argv[3], "%u", &mode))) {
		mode = 0;
		printf("Usage: random_packets <number> <length> <mode: 0=my MAC, 1=injection MAC> <delay in us>\n");
	} else if (mode > 1) {
		printf("Usage: random_packets <number> <length> <mode: 0=my MAC, 1=injection MAC> <delay in us>\n");
		return 1;
	}
	if (argc < 3 || (1 != sscanf(argv[2], "%u", &packet_size)))
		packet_size = 2200;
	if (argc < 2 || (1 != sscanf(argv[1], "%u", &num_packets)))
		num_packets = 10000;

	/* Generate packet payloads */
	printf("Generating packet payloads \n");
	payload_buffer = malloc(PAYLOAD_SIZE);
	if (payload_buffer == NULL) {
		perror("malloc payload buffer");
		exit(1);
	}
	generate_payloads(payload_buffer, PAYLOAD_SIZE);

	/* Setup the interface for lorcon */
	printf("Initializing LORCON\n");
	init_lorcon();

	/* Allocate packet */
	packet = malloc(sizeof(*packet) + packet_size);
	if (!packet) {
		perror("malloc packet");
		exit(1);
	}
	packet->fc = (0x08 /* Data frame */
				| (0x0 << 8) /* Not To-DS */);
	packet->dur = 0xffff;
	if (mode == 0) {
		memcpy(packet->addr1, "\x00\x16\xea\x12\x34\x56", 6);
		get_mac_address(packet->addr2, "mon0");
		memcpy(packet->addr3, "\x00\x16\xea\x12\x34\x56", 6);
	} else if (mode == 1) {
		memcpy(packet->addr1, "\x00\x16\xea\x12\x34\x56", 6);
		memcpy(packet->addr2, "\x00\x16\xea\x12\x34\x56", 6);
		memcpy(packet->addr3, "\xff\xff\xff\xff\xff\xff", 6);
	}
	packet->seq = 0;
	tx_packet.packet = (uint8_t *)packet;
	tx_packet.plen = sizeof(*packet) + packet_size;

	/* Send packets */
	printf("Sending %u packets of size %u (. every thousand)\n", num_packets, packet_size);

	timerThread();
	return 0;
}

static void handle()
{
	payload_memcpy(packet->payload, packet_size, (i*packet_size) % PAYLOAD_SIZE);
	// It is not the standard Sequence Control format
	packet->seq = i;
	ret = tx80211_txpacket(&tx, &tx_packet);

	if (ret < 0) {
		fprintf(stderr, "Unable to transmit packet: %s\n", tx.errstr);
		exit(1);
	}
	if (((i+1) % 1000) == 0) {
		printf(".");
		fflush(stdout);
	}
	if (((i+1) % 50000) == 0) {
		printf("%dk\n", (i+1)/1000);
		fflush(stdout);
	}
	if (i >= num_packets){
		exit(0);
	}

	i++;
}

static void timerThread()
{
	timer_t timer;
	
	struct sigevent evp;
	evp.sigev_value.sival_ptr = &timer;
	evp.sigev_notify = SIGEV_SIGNAL;
	evp.sigev_signo = SIGUSR1;

	struct itimerspec ts;
	ts.it_interval.tv_sec = 0;   
	ts.it_interval.tv_nsec = delay_us * 1000;
	ts.it_value.tv_sec = 1;  
	ts.it_value.tv_nsec = 0;

	signal(evp.sigev_signo, handle);

	ret = timer_create(CLOCK_REALTIME, &evp, &timer);
	if (ret) {
		perror("timer_create");
	}

	ret = timer_settime(timer, 0, &ts, NULL);
	if (ret) {
		perror("timer_settime");
	}

	while(1){
		/* wait for timer thread stop*/
	}
}

static void init_lorcon()
{
	/* Parameters for LORCON */
	int drivertype = tx80211_resolvecard("iwlwifi");

	/* Initialize LORCON tx struct */
	if (tx80211_init(&tx, "mon0", drivertype) < 0) {
		fprintf(stderr, "Error initializing LORCON: %s\n",
				tx80211_geterrstr(&tx));
		exit(1);
	}
	if (tx80211_open(&tx) < 0 ) {
		fprintf(stderr, "Error opening LORCON interface\n");
		exit(1);
	}

	/* Set up rate selection packet */
	tx80211_initpacket(&tx_packet);
}

