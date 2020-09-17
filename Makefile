export NAME?=count
export NAMESPACE?=count
export IMAGE?=matthewgall/count.re
export COLO:=$(shell kubectx -c)

.PHONY: apply apply-all
apply:
	@.utils/apply ${COLO}
apply-all:
	@.utils/apply all

.PHONY: delete delete-all
delete:
	@.utils/delete ${COLO}
delete-all:
	@.utils/delete all

.PHONY: rollout rollout-all
rollout:
	@.utils/rollout ${COLO}
rollout-all:
	@.utils/rollout all
