import os
from pathlib import Path

from rich import print

from bionty.dev._handle_sources import PUBLIC_SOURCES, parse_sources_yaml


def _upload_ontology_artifacts(
    instance: str, lamindb_user: str, lamindb_password: str, python_version: str = "3.9"
) -> None:
    """Uploads all ontology source file artifacts to the specified instance.

    Uses all files generated by nox that are found in the _dynamic folder.

    Args:
        instance: The lamindb instance to upload the files to.
        lamindb_user: The lamindb username.
        lamindb_password: The associated password of the lamindb user.
        python_version: The Python version that ran nox. Defaults to '3.9'.
    """
    import lamindb as ln

    _DYNAMIC_PATH = Path(
        f"{os.getcwd()}/.nox/build-package-bionty/lib/python{python_version}/site-packages/bionty/_dynamic"
    )

    ln.setup.login(lamindb_user, password=lamindb_password)
    ln.setup.load(instance, migrate=True)
    with ln.Session() as ss:
        transform = ln.select(
            ln.Transform, name="Bionty ontology artifacts"
        ).one_or_none()

        if transform is None:
            transform = ln.add(ln.Transform(name="Bionty ontology artifacts"))

        run = ln.Run(transform=transform)

        for filename in os.listdir(_DYNAMIC_PATH.absolute()):
            nox_ontology_file_path = os.path.join(_DYNAMIC_PATH.absolute(), filename)

            ontology_ln_file = ss.select(ln.File, name=filename).one_or_none()

            if ontology_ln_file is not None:
                print(
                    "[bold yellow]Found"
                    f" {ontology_ln_file.name}{ontology_ln_file.suffix} on S3."
                    " Skipping ingestion..."
                )
            else:
                ontology_ln_file = ln.File(
                    nox_ontology_file_path, key=filename, run=run
                )
                ss.add(ontology_ln_file)


all_public_versions = parse_sources_yaml(PUBLIC_SOURCES)
# nothing happens if no additional versions are added
if all_public_versions.shape[0] > 23:
    _upload_ontology_artifacts(
        instance="sunnyosun/bionty-assets",
        lamindb_user="testuser2@lamin.ai",
        lamindb_password="goeoNJKE61ygbz1vhaCVynGERaRrlviPBVQsjkhz",
        python_version="3.9",
    )
