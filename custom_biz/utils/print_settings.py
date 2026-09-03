import os
import base64
import mimetypes
from urllib.parse import urlparse
import frappe
from bs4 import BeautifulSoup
from frappe.utils.pdf import pdf_body_html as original_pdf_body_html


def embed_images_as_base64(html_str):
	"""Convert /files/ image references to inline base64 data URIs.
	If an image file is missing, replace with a transparent data URI to avoid wkhtmltopdf network 404 error.
	"""
	if not html_str:
		return html_str
	try:
		soup = BeautifulSoup(html_str, "html.parser")
		modified = False
		for img in soup.find_all("img"):
			src = img.get("src")
			if not src:
				continue
			parsed = urlparse(src)
			path = parsed.path
			if "/files/" in path:
				rel_path = path[path.find("/files/") :].lstrip("/")
				site_path = getattr(frappe.local, "site_path", None)
				if not site_path and hasattr(frappe, "get_site_path"):
					site_path = frappe.get_site_path()

				file_path = None
				if site_path:
					file_path = os.path.join(site_path, "public", rel_path)
					if not os.path.exists(file_path):
						file_path = os.path.join(site_path, rel_path)

				if file_path and os.path.exists(file_path):
					mime, _ = mimetypes.guess_type(file_path)
					with open(file_path, "rb") as f:
						b64 = base64.b64encode(f.read()).decode("utf-8")
					img["src"] = f"data:{mime or 'image/png'};base64,{b64}"
					modified = True
				else:
					img["src"] = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
					modified = True
		return str(soup) if modified else html_str
	except Exception:
		frappe.logger("pdf").error("Error embedding images as base64", exc_info=True)
		return html_str


def clean_header_footer_image_styles(html_str):
	"""Ensure header and footer images span 100% width with slightly reduced height."""
	if not html_str:
		return html_str
	try:
		soup = BeautifulSoup(html_str, "html.parser")
		modified = False
		for img in soup.find_all("img"):
			if img.has_attr("height"):
				del img["height"]
				modified = True
			img["style"] = "width: 100% !important; max-width: 100% !important; max-height: 24mm !important; object-fit: fill !important;"
			modified = True
		return str(soup) if modified else html_str
	except Exception:
		return html_str


def custom_pdf_body_html(template, args, **kwargs):
	# Ensure Print Settings has repeat_header_footer enabled
	try:
		if not frappe.db.get_single_value("Print Settings", "repeat_header_footer"):
			frappe.db.set_single_value("Print Settings", "repeat_header_footer", 1)
	except Exception:
		pass

	# Render standard body HTML first
	html = original_pdf_body_html(template, args, **kwargs)

	# If explicit no_letterhead requested, return embedded HTML as-is
	if args.get("no_letterhead"):
		return embed_images_as_base64(html)

	doc = args.get("doc")
	no_letterhead = args.get("no_letterhead")
	letterhead_name = args.get("letterhead") or (doc.get("letter_head") if doc else None)

	from frappe.www.printview import get_letter_head
	lh = get_letter_head(doc, no_letterhead, letterhead_name) or {}
	letter_head_content = args.get("letter_head") or lh.get("content") or ""
	footer_content = args.get("footer") or lh.get("footer") or ""

	letter_head_content = clean_header_footer_image_styles(letter_head_content)
	footer_content = clean_header_footer_image_styles(footer_content)

	soup = BeautifulSoup(html, "html.parser")

	# Add CSS to enforce full width header and footer images with slightly reduced height
	header_footer_style = soup.new_tag("style")
	header_footer_style.string = """
		.letter-head img, .letter-head-footer img {
			width: 100% !important;
			max-width: 100% !important;
			max-height: 24mm !important;
			object-fit: fill !important;
			display: block;
			margin: 0 auto;
		}
		.letter-head-footer {
			margin-bottom: 2px !important;
		}
		#footer-html p.page-number {
			margin-top: 2px !important;
			margin-bottom: 0px !important;
		}
	"""
	if soup.head:
		soup.head.append(header_footer_style)
	else:
		soup.insert(0, header_footer_style)

	# 1. Header Handling
	has_header = bool(soup.find(id="header-html"))
	if not has_header and letter_head_content:
		# Extract any static letter-head div outside header-html to avoid duplication on page 1 body
		for static_lh in soup.find_all(class_="letter-head"):
			if not static_lh.find_parent(id="header-html"):
				static_lh.extract()

		header_div = soup.new_tag("div", id="header-html", attrs={"class": "hidden-pdf"})
		header_inner_soup = BeautifulSoup(
			f'<div class="letter-head">{letter_head_content}</div>', "html.parser"
		)
		header_div.append(header_inner_soup)

		if soup.body:
			soup.body.insert(0, header_div)
		elif soup.find("div", class_="print-format"):
			soup.find("div", class_="print-format").insert(0, header_div)
		else:
			soup.insert(0, header_div)

	# 2. Footer Handling
	has_footer = bool(soup.find(id="footer-html"))
	if not has_footer:
		footer_div = soup.new_tag("div", id="footer-html", attrs={"class": "visible-pdf"})
		footer_inner = ""
		if footer_content:
			footer_inner += f'<div class="letter-head-footer">{footer_content}</div>'
		footer_inner += '<p class="text-center small page-number visible-pdf"><span class="page"></span> / <span class="topage"></span></p>'
		footer_inner_soup = BeautifulSoup(footer_inner, "html.parser")
		footer_div.append(footer_inner_soup)

		if soup.body:
			soup.body.append(footer_div)
		elif soup.find("div", class_="print-format"):
			soup.find("div", class_="print-format").append(footer_div)
		else:
			soup.append(footer_div)

	final_html = str(soup)
	return embed_images_as_base64(final_html)


def letter_head_before_save(doc, method=None):
	"""Clean up malformed image height styles in Letter Head HTML and enforce full width with slightly reduced height."""
	if doc.content:
		doc.content = clean_header_footer_image_styles(doc.content)
	if doc.footer:
		doc.footer = clean_header_footer_image_styles(doc.footer)
