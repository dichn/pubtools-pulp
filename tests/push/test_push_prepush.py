import os
import functools


from pubtools.pulplib import RpmUnit

from pubtools._pulp.tasks.push import entry_point

from .util import hide_unit_ids


def test_pre_push(
    fake_controller, data_path, fake_push, fake_state_path, command_tester
):
    """Test usage of --pre-push with all kinds of supported content."""
    # Sanity check that the Pulp server is, initially, empty.
    client = fake_controller.client
    assert list(client.search_content()) == []

    # Set it up to find content from our staging dir, which contains a mixture
    # of just about every content type
    stagedir = os.path.join(data_path, "staged-mixed")

    compare_extra = {
        "pulp.yaml": {
            "filename": fake_state_path,
            "normalize": hide_unit_ids,
        }
    }
    args = [
        "",
        # This option enables pre-push which should avoid making content
        # visible to end-users
        "--pre-push",
        "--source",
        "staged:%s" % stagedir,
        "--pulp-url",
        "https://pulp.example.com/",
    ]

    run = functools.partial(entry_point, cls=lambda: fake_push)

    # It should be able to run without crashing.
    command_tester.test(
        run,
        args,
        compare_plaintext=False,
        compare_extra=compare_extra,
    )

    # command_tester will have already compared pulp state against baseline,
    # but just to be explicit about it we will check here too...
    units = list(client.search_content())

    # It should have uploaded some stuff
    assert units

    for unit in units:
        # The only type of content is RPMs, because that's all we support for
        # pre-push right now
        assert isinstance(unit, RpmUnit)

        # And the only repo containing those RPMs should be all-rpm-content,
        # because that's how pre-push works
        assert unit.repository_memberships == ["all-rpm-content"]